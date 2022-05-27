from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('user-images', views.UserImagesView, basename='user-images')
router.register('all-images', views.AllImagesView, basename='all-images')

app_name = 'images'
urlpatterns = [
    path('', include(router.urls)),
    path('<slug>', views.temp_link, name='temp-link'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)