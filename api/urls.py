from django.urls import path , include
from api.views import *
from rest_framework.authtoken.views import ObtainAuthToken
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Parking Space Finder API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'parkzones', ParkZoneViewSet),
# router.register(r'search', ParkingZoneSearchView, basename='parkingzone-search')





urlpatterns = [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("register/user", UserRegistration.as_view(), name='user-register'),
    path("register/admin", AdminRegistration.as_view(), name='admin-register'),
    path('token/', ObtainAuthToken.as_view(), name='api_token_auth'),
    path('reserve/<int:pk>/',ReservationView.as_view(),name='reservation'),
    path('cancel-reservation/<int:pk>/', CancelReservationView.as_view(), name='cancel_reservation'),
    path('search/',ParkZoneSearchView.as_view(),name='search'),
    path('ticket/',TicketPdfView.as_view(),name='ticket'),
    path('checkout/<int:pk>/', CheckOutView.as_view(), name='checkout'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('',include(router.urls))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

