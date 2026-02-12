# shipments/mixins.py
import logging
from django.contrib.auth.mixins import AccessMixin

logger = logging.getLogger(__name__)


class RBACContextMixin(AccessMixin):
    """
    Mixin to provide Role-Based Access Control (RBAC) flags to the template context.
    Roles:
    - is_superadmin: Django Superuser (Full access + Admin Panel)
    - is_admin: Member of 'Admin' group (Full CRUD in frontend)
    - is_viewer: Member of 'Viewer' group (Read-only access)
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        is_superadmin = False
        is_admin = False
        is_viewer = False

        if user.is_authenticated:
            # SuperAdmin: Superuser status
            is_superadmin = user.is_superuser
            
            # Admin: Member of 'Admin' group or Superuser (Superusers naturally have Admin rights)
            is_admin = user.is_superuser or user.groups.filter(name='Admin').exists()
            
            # Viewer: Member of 'Viewer' group
            is_viewer = user.groups.filter(name='Viewer').exists()

        context['is_superadmin'] = is_superadmin
        context['is_admin'] = is_admin
        context['is_viewer'] = is_viewer
        
        # Professional helper: determines if user can perform CRUD
        context['can_edit'] = is_admin or is_superadmin

        return context
