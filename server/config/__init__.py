from .test import TestConfig
from .production import ProdConfig
from .staging import StagingConfig

try:
    from .development import DevConfig
except Exception as e:
    DevConfig = None

__all__ = ['DevConfig', 'TestConfig', 'ProdConfig', 'StagingConfig']
