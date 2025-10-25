from .api import api as api_views
from .user import user_views
from .index import index_views
from .auth import auth_views
from .admin import setup_admin
from .admin_api import admin_api

views = [
    user_views,
    index_views,
    auth_views,
    admin_api,
    api_views
] 