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
router.register(r'bike_park_zone', BikeParkZoneViewSet, basename='bikeparkzone')
router.register(r'car_park_zone', CarParkZoneViewSet, basename='carparkzone')
router.register(r'heavy_park_zone', HeavyParkZoneViewSet, basename='bikeparkzone')



urlpatterns = [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("register/user", UserRegistration.as_view(), name='user-register'),
    path("register/admin", AdminRegistration.as_view(), name='admin-register'),
    path('token/', ObtainAuthToken.as_view(), name='api_token_auth'),
    path('bike/reserve/',BikeReservationView.as_view(),name='bike-reservation'),
    path('car/reserve/',CarReservationView.as_view(),name='car-reservation'),
    path('heavy/reserve/',HeavyReservationView.as_view(),name='heavy-reservation'),
    path('search/bike/',BikeParkingZoneSearchView.as_view(),name='search-bike'),
    path('search/car/',CarParkingZoneSearchView.as_view(),name='search-car'),
    path('search/heavy/',HeavyParkingZoneSearchView.as_view(),name='search-heavy'),
    path('bike/ticket/',BikeTicketPdfView.as_view(),name='bike-ticket'),
    path('car/ticket/',CarTicketPdfView.as_view(),name='car-ticket'),
    path('heavy/ticket/',HeavyTicketPdfView.as_view(),name='heavy-ticket'),
    path('bike/checkout/', BikeCheckOutView.as_view(), name='bike-checkout'),
    path('car/checkout/', CarCheckOutView.as_view(), name='car-checkout'),
    path('heavy/checkout/', HeavyCheckOutView.as_view(), name='heavy-checkout'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('',include(router.urls))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

