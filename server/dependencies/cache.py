import json
import logging
import time
from functools import wraps
from operator import itemgetter

from eventlet.timeout import Timeout, with_timeout
from nameko.events import SERVICE_POOL, EventHandler

logger = logging.getLogger(" auth_cache")
CACHEBACK_ASYNC_TASK = " cacheback_async_task "
CACHEBACK_TIMEOUT = 300
CACHE_NAME = " cache "
EVENT_DISPATCHER_NAME = " dispatch "
MAX_EXPIRATION = 604800   # 1 week
REFRESH_TIMEOUT = 10
FETCH_ON_STALE_THRESHOLD = 3600


class FuzzyKeyDict (dict):

    def __getitem__(self, key):
        u""" Get key, the character and numeric type are trying to """

        try:
            return super(FuzzyKeyDict, self). __getitem__(key)
        except KeyError:
            if isinstance(key, str):
                return super(FuzzyKeyDict, self). __getitem__(int(key))
            else:
                return super(FuzzyKeyDict, self). __getitem__(str(key))

    def get(self, key, default=None):
        try:
            return self. __getitem__(key)
        except KeyError:
            return default


class JobConst (object):

    def __init__(self, lifetime=60, fetch_on_miss=True, default_result=None,
                 cache_name=CACHE_NAME, key_prefix=None,
                 fetch_on_stale_threshold=FETCH_ON_STALE_THRESHOLD,
                 event_dispatcher_name=EVENT_DISPATCHER_NAME,
                 cache_ttl=MAX_EXPIRATION):
        self.lifetime = lifetime
        self.fetch_on_miss = fetch_on_miss
        self.default_result = default_result
        self.cache_name = cache_name
        self.key_prefix = key_prefix
        self.fetch_on_stale_threshold = fetch_on_stale_threshold
        self.event_dispatcher_name = event_dispatcher_name
        self.cache_ttl = cache_ttl


class Job (object):

    def __init__(self, job_const):
        self.lifetime = job_const.lifetime
        self.fetch_on_miss = job_const.fetch_on_miss
        self.default_result = job_const.default_result
        self.cache_name = job_const.cache_name
        self.key_prefix = job_const.key_prefix
        self.fetch_on_stale_threshold = job_const.fetch_on_stale_threshold
        self.event_dispatcher_name = job_const.event_dispatcher_name
        self.cache = None
        self.service = None
        self.event_dispatcher = None
        self.cache_ttl = job_const.cache_ttl

    def set_service(self, service):
        self.service = service
        if self.key_prefix is None:
            self.key_prefix = self.service.name

        cache = getattr(self.service, self.cache_name, None)
        if not cache:
            raise Exception(" invalid cache_name ")
        else:
            self.cache = cache

        event_dispatcher = getattr(
            self.service, self.event_dispatcher_name, None)
        if not event_dispatcher:
            raise Exception(" invalid event_dispatcher_name ")
        else:
            self.event_dispatcher = event_dispatcher

    def set_func(self, func):
        self.func = func

    def key(self, * args, ** kwargs):
        """
        Returns a unique string based on the argument
        Currently supported parameters are:
            Basic type:
                string, integer, boolean
            There are also queues, tuples
        """
        func = self.func
        func_name = " % s : % s : % s " % (
            self.key_prefix, func. __module__, func. __name__)
        if not args and not kwargs:
            return func_name
        try:
            def _default_list_key(lt):
                ret = []
                for p in lt:
                    if isinstance(p, list):
                        ret.append(tuple(p))
                    else:
                        ret.append(p)
                return tuple(ret)

            n_args = _default_list_key(args)
            if args and not kwargs:
                return " % s : % s " % (func_name, str(hash(n_args)))

            sorted_kwargs = sorted(kwargs.iteritems(), key=itemgetter(0))
            keys = _default_list_key(map(itemgetter(0), sorted_kwargs))
            values = _default_list_key(map(itemgetter(1), sorted_kwargs))

            return " % s : % s : % s : % s " % (
                func_name, hash(n_args), hash(tuple(keys)),
                hash(tuple(values)))
        except TypeError:
            logger.exception(" key: args: % s , kwargs: % s ", args, kwargs)
            raise RuntimeError(
                " Unable to generate cache key due to unhashable "
                " args or kwargs - you need to implement your own "
                " key generation method to avoid this problem ")

    def cache_get(self, key):
        ret = self.cache.get(key)
        if ret:
            expiry, value = ret.split(" , ", 1)
            return float(expiry), json.loads(value)
        return ret

    def cache_set(self, key, expiry, value):
        self.cache.set(key, " % s , % s " % (expiry, json.dumps(value)),
                       ex=self.cache_ttl)

    def fetch(self, * args, ** kwargs):
        func = self.func
        result = self.default_result
        key = None
        try:
            key = self.key(* args, ** kwargs)
            result = func(self.service, * args, ** kwargs)

            if result == " CACHEBACK_USE_STALE_FLAG ":
                cache_result = self.cache_get(key)
                if cache_result:
                    result = cache_result[1]
                else:
                    result = self.default_result
                expiry = self.temp_cache_expire()
            else:
                expiry = time.time() + self.lifetime

            self.cache_set(key, expiry, result)
        except Exception as e:
            logger.exception(
                " cacheback fetch error, key: % s , func: % s , args: % s , "
                " kwargs: % s, error: %s ", key, func, args, kwargs, e)
        return result

    def async_fetch(self, * args, ** kwargs):
        func = self.func
        payload = {" func ": func. __name__, " args ": args,
                   " kwargs ": kwargs, " lifetime ": self.lifetime}
        if self.cache_name != CACHE_NAME:
            payload[" cache_name "] = self.cache_name
        self.event_dispatcher(CACHEBACK_ASYNC_TASK, payload)

    def get(self, * args, ** kwargs):
        key = self.key(* args, ** kwargs)
        ret = None
        item = self.cache_get(key)

        if item is None:
            if self.fetch_on_miss:
                logger.debug(" key: % s miss cache, running sync job ", key)
                ret = self.fetch(* args, ** kwargs)
            else:
                logger.debug(" key: % s miss cache, set default_result: % s , "
                             " running async job ", key, self.default_result)
                self.cache_set(key, self.temp_cache_expire(),
                               self.default_result)
                self.async_fetch(* args, ** kwargs)
                ret = self.default_result
        else:
            expiry, ret = item

            delta = time.time() - expiry
            if delta > 0:
                # Cache HIT but STALE expiry - we can either either:
                # a) fetch the data immediately, blocking execution until
                #     the fetch has finished, or
                # b) trigger a refresh but allow the stale result to be
                #     returned this time. This is only acceptable
                if delta > self.fetch_on_stale_threshold - self.lifetime:
                    logger.debug(
                        " key: % s stale cache, running sync job ", key)
                    ret = self.fetch(* args, ** kwargs)
                else:
                    logger.debug(
                        " key: % s stale cache, set pre result: % s , "
                        " running async job ", key, ret)
                    self.cache_set(key, self.temp_cache_expire(), ret)
                    self.async_fetch(* args, ** kwargs)
            else:
                logger.debug(" key: % s cache HIT ", key)

        return ret

    def temp_cache_expire(self):
        return time.time() + REFRESH_TIMEOUT

    def invalidate(self, service, * args, ** kwargs):
        """
        Mark a cached item invalid and trigger an asynchronous
        job to refresh the cache
        """
        self.set_service(service)
        key = self.key(* args, ** kwargs)
        item = self.cache_get(key)
        logger.debug(" invalidate cache key: % s ", key)
        if item is not None:
            expiry, data = item
            self.cache_set(key, self.temp_cache_expire(), data)
            self.async_fetch(* args, ** kwargs)

    def delete(self, service, * args, ** kwargs):
        """ Remove an item from the cache """
        self.set_service(service)
        key = self.key(* args, ** kwargs)
        logger.debug(" delete cache key: % s ", key)
        self.cache.delete(key)


class BatchFunctionJob (Job):

    def key(self, * args, ** kwargs):
        single_key = kwargs.pop(" single_key ")
        k = super(BatchFunctionJob, self) .key(* args, ** kwargs)
        if isinstance(single_key, int):
            key_type = 1
        elif isinstance(single_key, basestring):
            key_type = 2
        else:
            raise Exception(
                " BatchFunctionJob query key type error, key: % s , "
                " type: % s ", single_key, type(single_key))
        return " % s : % s : % s " % (k, single_key, key_type)

    def key2arg(self, k):
        """ from the key string back to the original single_key,
         but the string type """
        hash_key, query_key, key_type = k.rsplit(" : ", 2)
        if key_type == " 1 ":
            return int(query_key)
        return query_key

    def cache_get_many(self, keys):
        cache_ret = self.cache.mget(keys)
        ret = {}
        for k, v in zip(keys, cache_ret):
            if v:
                expiry, value = v.split(" , ", 1)
                ret[k] = float(expiry), json.loads(value)
            else:
                ret[k] = v
        return ret

    def cache_set_mamy(self, data):
        pl = self.cache.pipeline(transaction=False)
        for key, (expiry, value) in data.items():
            pl.set(key, " % s , % s " %
                   (expiry, json.dumps(value)), ex=self.cache_ttl)
        pl.execute()

    def fetch(self, * args, ** kwargs):
        func = self.func
        result = func(self.service, * args, ** kwargs)
        query_keys = args[0]
        n_args = args[1:]
        data = {}
        cache_ret = {}
        timeout = self.temp_cache_expire()
        keys = [self.key(single_key=k, * n_args, ** kwargs)
                for k in query_keys]

        if result == " CACHEBACK_USE_STALE_FLAG ":
            cache_result = self.cache_get_many(keys)
            result = {}
            for key, item in cache_result.items():
                if item:
                    expiry, value = item
                else:
                    value = self.default_result
                result[key] = value
            expiry = timeout
        else:
            expiry = time.time() + self.lifetime
        for k, cache_key in zip(query_keys, keys):
            if k not in result:
                single_value = self.default_result
                # to be written in the cache
                data[cache_key] = (timeout, single_value)
            else:
                single_value = result.get(k)
                data[cache_key] = (expiry, single_value)
            cache_ret[k] = single_value
        self.cache_set_mamy(data)
        return cache_ret

    def get(self, * args, ** kwargs):
        # Arrow the original batch query array, construct the key array
        query_keys = args[0]
        if not query_keys:
            return {}
        n_args = args[1:]
        keys = [self.key(single_key=k, * n_args, ** kwargs)
                for k in query_keys]
        items = self.cache_get_many(keys)
        new_keys = filter(lambda k: not items[k], keys)
        timeout = self.temp_cache_expire()
        now = time.time()
        sync_keys = []   # part of the query cache is not hit, need to block
        async_keys = []   # hit, but need to update the cache asynchronously
        async_data = {}
        cache_ret = FuzzyKeyDict()
        if new_keys:
            # Block execution
            if self.fetch_on_miss:
                logger.debug(
                    " keys: % s miss cache, running sync job ", new_keys)
                sync_keys.extend(new_keys)
            else:

                logger.debug(
                    " keys: % s miss cache, set default_result: % s , "
                    " running async job ", new_keys, self.default_result)
                for k in new_keys:
                    async_data[k] = (timeout, self.default_result)
                    cache_ret[self.key2arg(k)] = self.default_result
                async_keys.extend(new_keys)

        for key, item in items.iteritems():
            if not item:
                continue
            expiry, data = item
            delta = now - expiry
            if delta > 0:   # has expired
                if delta > self.fetch_on_stale_threshold - self.lifetime:
                    # If the longest expiration time of the asynchronous
                    # execution time is reached, the execution is blocked
                    logger.debug(
                        " key: % s stale cache, running sync job ", key)
                    sync_keys.append(key)
                else:
                    # If the maximum expiration time is not set, it will be
                    # executed asynchronously
                    async_keys.append(key)
                    async_data[key] = (timeout, data)
                    cache_ret[self.key2arg(key)] = data
            else:
                cache_ret[self.key2arg(key)] = data
        if async_keys:
            logger.debug(
                " keys ' % s ' - triggering async refresh and returning "
                " stale result ", async_keys)
            # Save the old data temporarily
            self.cache_set_mamy(async_data)
            self.async_fetch(map(self.key2arg, async_keys),
                             * n_args, ** kwargs)
        if sync_keys:
            logger.debug(
                " keys ' % s ' - running synchronous refresh ", sync_keys)
            ret = self.fetch(map(self.key2arg, sync_keys),
                             * n_args, ** kwargs)
            cache_ret.update(ret)
        if not sync_keys and not async_keys:
            logger.debug(" keys ' % s ' - cache HIT ", keys)
        return cache_ret

    def delete(self, service, * args, ** kwargs):
        self.set_service(service)
        query_keys = args[0]
        if not query_keys:
            return
        n_args = args[1:]
        keys = [self.key(single_key=k, * n_args, ** kwargs)
                for k in query_keys]
        pl = self.cache.pipeline(transaction=False)
        for k in keys:
            pl.delete(k)
        pl.execute()


def greenthread_cacheback(lifetime=60, fetch_on_miss=True, default_result=None,
                          cache_name=CACHE_NAME, key_prefix=None,
                          fetch_on_stale_threshold=FETCH_ON_STALE_THRESHOLD,
                          event_dispatcher_name=EVENT_DISPATCHER_NAME,
                          cache_ttl=MAX_EXPIRATION):
    """
    Decorate function to cache its return value.
    ** Example **:
    .. code-block :: python
        from nameko.events import EventDispatcher
        from nameko_cacheback import (CachebackEventHandlerMixin,
                                      greenthread_cacheback
        class YourNamekoService (CachebackEventHandlerMixin):
            dispatch = EventDispatcher () # required
            cache = Redis ("cacheback") # required namek-redis
            @greenthread_cacheback (lifetime = 60, cache_name = "cache")
            def you_svr_func (self, * args):
                balabala
    : param lifetime: Default cache lifetime is 1 minutes.
        After this time, the result will be considered stale and
        requests will trigger a job to refresh it
    : param fetch_on_miss: Whether to perform a synchronous refresh
        when a result is missing from the cache
        Default behaviour is to do a synchronous fetch when the cache is empty.
        Stale results are uniform ok, but no no results
    : param default_result: Default return result
    : param cache_name: Default `` cache``, nameko service's attribute.
    : param key_prefix: Default service name, cache key prefix
    : param fetch_on_stale_threshold: Whether to perform a synchronous refresh
        when a result is in the cache
    : param event_dispatcher_name: Default `dispatch`, nameko service attribute
    """
    job_const = JobConst(lifetime, fetch_on_miss, default_result, cache_name,
                         key_prefix, fetch_on_stale_threshold,
                         event_dispatcher_name, cache_ttl)

    def _wrapper(func):
        @wraps(func)
        def __wrapper(self, * args, ** kwargs):
            job = Job(job_const)
            job.set_service(self)
            job.set_func(func)
            return job.get(* args, ** kwargs)
        __wrapper.fn = func
        __wrapper.job_klass = Job
        __wrapper.job_const = job_const

        return __wrapper
    return _wrapper


cacheback = greenthread_cacheback


def multi_cacheback(lifetime=60, fetch_on_miss=True, default_result=None,
                    cache_name=CACHE_NAME, key_prefix=None,
                    fetch_on_stale_threshold=FETCH_ON_STALE_THRESHOLD,
                    event_dispatcher_name=EVENT_DISPATCHER_NAME,
                    cache_ttl=MAX_EXPIRATION, batch_limit=50):
    job_const = JobConst(lifetime, fetch_on_miss, default_result, cache_name,
                         key_prefix, fetch_on_stale_threshold,
                         event_dispatcher_name, cache_ttl)

    def _wrapper(func):
        @wraps(func)
        def __wrapper(self, * args, ** kwargs):
            job = BatchFunctionJob(job_const)
            job.set_service(self)
            job.set_func(func)
            query_keys = args[0]
            n_args = args[1:]
            cache_ret = FuzzyKeyDict()
            subs_keys = [query_keys[x: x + batch_limit]
                         for x in xrange(0, len(query_keys), batch_limit)]
            for sub_keys in subs_keys:
                cache_tmp = job.get(sub_keys, * n_args, ** kwargs)
                cache_ret.update(cache_tmp)
            return cache_ret
        __wrapper.fn = func
        __wrapper.job_klass = BatchFunctionJob
        __wrapper.job_const = job_const

        return __wrapper
    return _wrapper


class CachebackEventHandler (EventHandler):

    def setup(self):
        self.source_service = self.container.service_name
        super(CachebackEventHandler, self) .setup()


class CachebackEventHandlerMixin (object):

    @ CachebackEventHandler.decorator(" ", CACHEBACK_ASYNC_TASK, SERVICE_POOL)
    def cacheback_async_task_dispatch(self, payload):
        func_name = payload[" func "]
        args = payload[" args "]
        kwargs = payload[" kwargs "]
        func = getattr(self, func_name)

        try:
            job = func.job_klass(func.job_const)
            job.set_service(self)
            job.set_func(func.fn)
            with_timeout(CACHEBACK_TIMEOUT, job.fetch, * args, ** kwargs)

        except Timeout:
            logger.exception(" cacheback async fetch error, func: % s , "
                             " args: % s , kwargs: % s ", func, args, kwargs)
