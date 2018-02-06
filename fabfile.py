# -*- coding: utf-8 -*- ##

import uuid
from fabric.api import env, prompt, local


def source_settings():
    env.SOURCE_PATH = '/zapcore'
    env.colorize_errors = True
    env.git_path = 'git@github.com:ojengwa/zapcore.git'
    env.AWS_ACCESS_KEY = 'AKIAIFUHSUNLQERBEPYQ'
    env.AWS_ACCESS_SECRET = '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'


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


def dev_server():
    local('python manage.py runserver')


def test():
    local('python manage.py test')


def assets():
    local('python manage.py collectstatic')


def init():
    source_settings()
    local('zappa init')


def deploy(environment=''):
    source_settings()
    local('zappa deploy {0}'.format(environment))


def undeploy(environment='', remove_logs=False):
    source_settings()
    if remove_logs:
        cmd = 'zappa undeploy {0} --remove-logs'.format(environment)
    else:
        cmd = 'zappa undeploy {0}'.format(environment)

    local(cmd)


def update(environment=''):
    source_settings()
    local('zappa update {0}'.format(environment))


def rollback(environment='', revisions=1):
    source_settings()
    local('zappa rollback {0} -n {1}'.format(environment, revisions))


def schedule(environment=''):
    source_settings()
    local('zappa schedule {0}'.format(environment))


def unschedule(environment=''):
    source_settings()
    local('zappa unschedule {0}'.format(environment))


def pack(environment='', storage_path='{0}.zip'.format(uuid.uuid4())):
    source_settings()
    local('zappa package {0} -o {1}'.format(environment, storage_path))


def cloudformation(lambda_arn, role_arn, environment=''):
    source_settings()
    local(
        'zappa template {0} --l {1} -r {2}'.format(
            lambda_arn, role_arn, environment))


def status(environment=''):
    source_settings()
    local('zappa status {0}'.format(environment))


def log(environment='', events='', since=''):
    source_settings()
    local('zappa tail {0} --{1} --since'.format(environment, events, since))


def invoke(cmd, environment='', verbose=True):
    source_settings()

    if verbose:
        text = 'zappa invoke {0} --{1} --raw'.format(environment, cmd)
    else:
        text = 'zappa invoke {0} --{1}'.format(environment, cmd)

    local(text)
