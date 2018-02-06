# -*- coding: utf-8 -*- ##

import os
from fabric.api import env, run, sudo, require, prompt, put


def source_settings():
    env.SOURCE_PATH = 'src/zapcore'
    env.git_path = 'git@github.com:ojengwa/zapcore.git'


def render_put(template_name, dest, params, mode=None, tempfile='tempfile'):
    pass
    # data = loader.render_to_string(template_name, dictionary=params)
    # open(tempfile, 'w').write(data)
    # put(tempfile, dest, mode)
    # os.remove(tempfile)


def ifnotsetted(key, default, is_prompt=False, text=None, validate=None):
    if not (key in env and env[key]):
        if is_prompt:
            prompt(text, key, default, validate)
        else:
            env['key'] = default


def prompts():
    source_settings()
    ifnotsetted('host_string', 'truckica.com', True,
                "No hosts found. Please specify "
                "single host string for connection")
    ifnotsetted('user', 'root', True, "Server user name")
    ifnotsetted('VPS_IP', '97.107.129.224', True, "VPS IP")
    ifnotsetted('POSTGRES_USER', 'truckica', True, "PostgreSQL user name")
    ifnotsetted('POSTGRES_PASSWORD', 'truckicaS3n89mkk',
                True, "PostgreSQL user's password")
    ifnotsetted('POSTGRES_DB', 'truckica', True, "PostgreSQL DATABASE")
    ifnotsetted('UBUNTU_VERSION', 'karmic', True, "Ubuntu version name")
    ifnotsetted('PAYPAL_EMAIL',
                'admin_1255085897_biz@crowdsense.com', True, "PAYPAL EMAIL")
    ifnotsetted('PAYPAL_TEST', 'True', True,
                "PAYPAL TEST (True or False)?", r'^(True|False)$')


def common_settings():
    source_settings()


def stage_settings():
    common_settings()


def production_settings():
    common_settings()


def server_setup():
    pass


def project_setup():
    pass


def setup_stage():
    stage_settings()


def setup_production():
    production_settings()


def update_stage():
    stage_settings()


def update_production():
    production_settings()


def rollback_stage():
    stage_settings()


def rollback_production():
    production_settings()


def release_stage():
    stage_settings()


def release_production():
    production_settings()
