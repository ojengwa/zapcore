from .test import TestConfig
from .production import ProdConfig
from .heroku import HerokuConfig

try:
    from .development import DevConfig
except Exception as e:
    DevConfig = None

__all__ = ['DevConfig', 'TestConfig', 'ProdConfig', 'HerokuConfig']
