# blue prints are imported 
# explicitly instead of using *
from .user import user_views
from .index import index_views
from .auth import auth_views
from .admin import setup_admin
from .transport import transport_views


views = [user_views, index_views, auth_views, transport_views] 
# blueprints must be added to this list