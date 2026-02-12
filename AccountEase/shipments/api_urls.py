from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ShipmentViewSet, LoginAPIView

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'shipments', ShipmentViewSet, basename='api-shipment')

# The API URLs are determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginAPIView.as_view(), name='api-login'),
]
