from django.utils.deprecation import MiddlewareMixin

from .controllers import home, map_page, store_list_page
from .models import Notification


class AdminErrorNotificationMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if request.path.startswith("/static/") or request.path.startswith("/media/"):
            return None
        Notification.objects.create(
            level="error",
            title="Server Error",
            message=str(exception)[:1000],
            path=request.path[:255],
            method=request.method[:10],
            status_code=500,
        )
        return None

    def process_response(self, request, response):
        if response.status_code == 404:
            if request.path.startswith("/static/") or request.path.startswith("/media/"):
                return response
            Notification.objects.create(
                level="warning",
                title="Not Found",
                message="URL not found",
                path=request.path[:255],
                method=request.method[:10],
                status_code=404,
            )
        return response


__all__ = ['home', 'store_list_page', 'map_page', 'AdminErrorNotificationMiddleware']
