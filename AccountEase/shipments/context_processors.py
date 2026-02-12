def rbac_flags(request):
    """
    Global context processor to provide RBAC flags to all templates.
    """
    user = request.user
    
    if not user.is_authenticated:
        return {
            "is_superadmin": False,
            "is_admin": False,
            "is_viewer": False,
            "can_edit": False
        }

    is_superadmin = user.is_superuser
    is_admin = user.is_superuser or user.groups.filter(name="Admin").exists()
    is_viewer = user.groups.filter(name="Viewer").exists()

    return {
        "is_superadmin": is_superadmin,
        "is_admin": is_admin,
        "is_viewer": is_viewer,
        "can_edit": is_admin or is_superadmin
    }
