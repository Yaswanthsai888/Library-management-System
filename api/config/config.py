"""Configuration settings for the Library Management System."""

class Config:
    """Base configuration."""
    API_KEY = "podapati@1"
    MAX_BOOKS_PER_PAGE = 20
    MIN_BOOKS_PER_PAGE = 1
    DEBUG = False

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    pass

# Map configuration names to objects
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
