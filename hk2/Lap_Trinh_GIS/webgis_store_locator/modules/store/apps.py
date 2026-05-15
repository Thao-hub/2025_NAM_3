from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.store'
    label = 'gis_store'
    verbose_name = 'Hệ thống quản lý cửa hàng'
