from django.contrib import admin
from django.urls import path
from bmstu_lab.migrations import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.GetAppointments),
    path('appointment/<int:id>/', views.GetAppointment, name='appointment'),
    path('search', views.GetQuery, name='search'),
]