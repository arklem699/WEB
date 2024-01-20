from django.contrib import admin
from django.urls import path
from bmstu_lab import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.GetAppointments),
    path('appointment/<int:id>/', views.GetAppointment, name='appointment_url'),
    path('find', views.GetQuery, name='find'),
    path('delete/<int:id>/', views.DeleteAppointment, name='delete_appoinment')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)