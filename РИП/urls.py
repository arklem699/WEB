"""
URL configuration for РИП project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from bmstu_lab import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.GetAppointments),
    path('appointment/<int:id>/', views.GetAppointment, name='appointment_url'),
    path('find', views.GetQuery, name='find'),
    path('delete/<int:id>/', views.DeleteAppointment, name='delete_appoinment'),
    path('', include(router.urls)),
    path(r'appointments/', views.get_list_appointment, name='appointments-list'),
    path(r'appointments/post/', views.post_list_appoinment, name='appointments-post'),
    path(r'appointments/post/<int:id>', views.post_appoinment_in_application, name='appointments-application-post'),
    path(r'appointments/<int:id>/', views.get_detail_appointment, name='appointments-detail'),
    path(r'appointments/<int:id>/put/', views.put_detail_appointment, name='appointments-put'),
    path(r'appointments/<int:id>/delete/', views.delete_detail_appointment, name='appointments-delete'),
    path(r'applications/', views.get_list_application, name='applications-list'),
    path(r'applications/<int:id>/', views.get_detail_application, name='applications-detail'),
    path(r'applications/<int:id>/delete/', views.delete_detail_application, name='applications-delete'),
    path(r'applications/<int:id>/user/put/', views.put_status_user_application, name='appointments-user-put'),
    path(r'applications/<int:id>/moderator/put/', views.put_status_moderator_application, name='appointments-moderator-put'),
    path(r'appapps/<int:id>/delete/', views.delete_appointment_from_application, name='appapps-delete'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)