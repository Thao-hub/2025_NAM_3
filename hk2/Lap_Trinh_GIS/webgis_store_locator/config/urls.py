from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound

urlpatterns = [
    path(
        ".well-known/appspecific/com.chrome.devtools.json",
        lambda request: HttpResponse("", content_type="application/json"),
        name="chrome_devtools",
    ),
    path(
        "favicon.ico",
        lambda request: HttpResponse(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
            '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0" stop-color="#0f766e"/><stop offset="1" stop-color="#14b8a6"/>'
            "</linearGradient></defs>"
            '<rect width="64" height="64" rx="14" fill="url(#g)"/>'
            '<path d="M18 34c0-8 6-14 14-14h14v6H32c-4.4 0-8 3.6-8 8s3.6 8 8 8h10v6H32c-8 0-14-6-14-14Z" fill="#ffffff"/>'
            "</svg>",
            content_type="image/svg+xml",
        ),
        name="favicon",
    ),
    path('', include('modules.store.urls')),
    path('tools/', include('modules.spatial.urls')),
    # test 404 page when DEBUG=True
    path('404-test/', lambda request: HttpResponseNotFound(render(request, '404.html'))),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
