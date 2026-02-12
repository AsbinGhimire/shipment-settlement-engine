from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from shipments.views import home

urlpatterns = [

     # Public Home Page
    path('', home, name='home'),

    # ------------------------------
    # Admin site
    # ------------------------------
    path('admin/', admin.site.urls),

    # ------------------------------
    # Authentication
    # ------------------------------
    path('login/', auth_views.LoginView.as_view(template_name='forgotapp/login_form.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # ------------------------------
    # Shipments app
    # ------------------------------
    path(
        'shipments/',
        include(('shipments.urls', 'shipments'), namespace='shipments')
    ),


    path('forgotapp/', include('forgotapp.urls')),

    # ------------------------------
    # API v1
    # ------------------------------
    path('api/v1/', include('shipments.api_urls')),
]

# ------------------------------
# Serve uploaded media files during development
# ------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
