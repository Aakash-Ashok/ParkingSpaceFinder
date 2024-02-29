from django.urls import path
from api.views import *
from rest_framework.authtoken.views import ObtainAuthToken
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter



router = DefaultRouter()
router.register(r'bike_park_zone', BikeParkZoneViewSet, basename='bikeparkzone')



urlpatterns = [
    path("register/user", UserRegistration.as_view(), name='user-register'),
    path("register/admin", AdminRegistration.as_view(), name='admin-register'),
    path('token/', ObtainAuthToken.as_view(), name='api_token_auth'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += router.urls
