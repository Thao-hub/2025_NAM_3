def store_shell(request):
    from .controllers import (
        _admin_header_notifications,
        _cart_items,
        _get_customer_profile,
        _is_admin_user,
        _user_header_notifications,
    )

    cart_total_quantity = 0
    profile_avatar_url = ""
    user_notifications = []
    show_admin_link = False
    notifications_url = ""

    try:
        cart_total_quantity = _cart_items(request)[1]
    except Exception:
        cart_total_quantity = 0

    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        try:
            profile = _get_customer_profile(user)
            if profile.avatar:
                profile_avatar_url = profile.avatar.url
        except Exception:
            profile_avatar_url = ""

        try:
            if _is_admin_user(user):
                user_notifications = _admin_header_notifications()
                notifications_url = "/admin/notifications/"
            else:
                user_notifications = _user_header_notifications(user)
                notifications_url = "/notifications/"
        except Exception:
            user_notifications = []
            notifications_url = ""

        try:
            show_admin_link = _is_admin_user(user)
        except Exception:
            show_admin_link = False

    return {
        "shell_cart_total_quantity": cart_total_quantity,
        "shell_profile_avatar_url": profile_avatar_url,
        "shell_user_notifications": user_notifications,
        "shell_show_admin_link": show_admin_link,
        "shell_notifications_url": notifications_url,
    }
