from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import (
    ShipmentListView,
    ShipmentCreateView,
    ShipmentUpdateView,
    ShipmentDeleteView,
    HelpLineView,
    ReportsView,
    ClientsView,
    get_chitti_files,
)


app_name = 'shipments'

urlpatterns = [

    # ------------------------------
    # Shipment CRUD
    # ------------------------------
    path('', ShipmentListView.as_view(), name='shipment_list'),
    path('add/', ShipmentCreateView.as_view(), name='add_shipment'),
    path('edit/<int:pk>/', ShipmentUpdateView.as_view(), name='edit_shipment'),
    path('delete/<int:pk>/', ShipmentDeleteView.as_view(), name='delete_shipment'),

    # ------------------------------
    # Yatayat Chitti AJAX (✅ WORKING)
    # ------------------------------
    path(
        'shipment-files/<int:shipment_id>/',
        get_chitti_files,
        name='get_chitti_files'
    ),

    # ------------------------------
    # Pages
    # ------------------------------
    path('helpline/', HelpLineView.as_view(), name='helpline'),
    path('reports/', ReportsView.as_view(), name='reports'),
    path('clients/', ClientsView.as_view(), name='clients'),

    # ------------------------------
    # Logout
    # ------------------------------
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]
