from .auth import auth_bp
from .provider import provider_bp
from .admin import admin_bp
from .customer import customer_bp

__all__ = ['auth_bp', 'provider_bp', 'admin_bp', 'customer_bp']
