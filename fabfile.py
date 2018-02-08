# -*- coding: utf-8 -*- ##

import uuid

from contextlib import contextmanager
from fabric.api import env, prompt, local
from fabric.context_managers import lcd as cd, shell_env


def source_settings():
    env.SOURCE_PATH = '/zapcore'
    env.colorize_errors = True
    env.git_path = 'git@github.com:ojengwa/zapcore.git'


def ifnotsetted(key, default, is_prompt=False, text=None, validate=None):
    if not (key in env and env[key]):
        if is_prompt:
            prompt(text, key, default, validate)
        else:
            env['key'] = default


def prompts():
    source_settings()
    ifnotsetted('DATABASE_URL', '', True, "Database URL")


def common_settings():
    source_settings()


@contextmanager
def zappa_env():
    orig_shell = env['shell']
    env_vars_str = ' '.join('{0}={1}'.format(key, value)
                            for key, value in env.items())
    env['shell'] = '{0} {1}'.format(env_vars_str, orig_shell)
    yield
    env['shell'] = orig_shell


def dev_server():
    local('python manage.py runserver')


def test():
    local('python manage.py test')


def assets(environment, node_env='production'):

    with cd('./client'), shell_env(
            NODE_ENV='{0}'.format(node_env),
            FLASK_ENV=environment):
        local('npm run build')
    local('python manage.py collectstatic')


def init():
    common_settings()
    with zappa_env():
        local('zappa init')


def deploy(environment='--all'):
    common_settings()
    with zappa_env():
        local('zappa deploy {0}'.format(environment))


def undeploy(environment, remove_logs=False):
    source_settings()
    if remove_logs:
        cmd = 'zappa undeploy {0} --remove-logs'.format(environment)
    else:
        cmd = 'zappa undeploy {0}'.format(environment)

    with zappa_env():
        local(cmd)


def update(environment):
    common_settings()
    with zappa_env():
        assets(environment)
        local('zappa update {0}'.format(environment))


def rollback(environment, revisions=1):
    common_settings()
    with zappa_env():
        local('zappa rollback {0} -n {1}'.format(environment, revisions))


def schedule(environment):
    common_settings()
    with zappa_env():
        local('zappa schedule {0}'.format(environment))


def unschedule(environment):
    common_settings()
    with zappa_env():
        local('zappa unschedule {0}'.format(environment))


def pack(environment, storage_path='{0}.zip'.format(uuid.uuid4())):
    common_settings()
    with zappa_env():
        local('zappa package {0} -o {1}'.format(environment, storage_path))


def cloudformation(lambda_arn, role_arn, environment):
    common_settings()
    with zappa_env():
        local(
            'zappa template {0} --l {1} -r {2}'.format(
                environment, lambda_arn, role_arn))


def status(environment):
    common_settings()
    with zappa_env():
        local('zappa status {0}'.format(environment))


def log(environment, events='', since='30m'):
    common_settings()
    with zappa_env():
        local(
            'zappa tail {0} {1} --since {2}'.format(
                environment, events, since))


def invoke(environment, cmd, verbose=True):
    common_settings()

    if verbose:
        text = 'zappa invoke {0} --{1} --raw'.format(environment, cmd)
    else:
        text = 'zappa invoke {0} --{1}'.format(environment, cmd)

    with zappa_env():
        local(text)
