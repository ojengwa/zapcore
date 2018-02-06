# -*- coding: utf-8 -*- ##

import os
from fabric.api import env, run, sudo, require, prompt, put, local


def source_settings():
    env.SOURCE_PATH = 'src/zapcore'
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


def stage_settings():
    common_settings()


def production_settings():
    common_settings()


def dev_setup():
    local('pythoN')


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
