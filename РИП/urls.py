from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import routers, permissions
from bmstu_lab import views

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet, basename='user')

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('', include(router.urls)),

    path('appointments/', views.get_list_appointment, name='appointments-list'),
    path('appointments/post/', views.post_list_appointment, name='appointments-post'),
    path('appointment/<int:id>/', views.detail_appointment, name='appointment-detail'),
    path('appointment/<int:id>/update/', views.update_appointment, name='appointment-update'),
    path('appointment/<int:id>/image/get/', views.get_image_appointment, name='appointment-image-get'),
    path('appointment/<int:id>/image/add/', views.add_image_appointment, name='appointment-image-add'),

    path('applications/', views.get_list_applications, name='applications-list'),
    path('application/user/', views.get_list_user_application, name='application-user'),
    path('application/<int:id>/', views.detail_application, name='application-detail'),
    path('application/<int:id>/delete/', views.delete_application, name='application-delete'),
    path('application/<int:id>/user/put/', views.put_status_user_application, name='applications-user-put'),
    path('application/<int:id>/moderator/put/', views.put_status_moderator_application, name='applications-moderator-put'),

    path('appapp/async/put/', views.put_async_was_appapp, name='appapp-async-put'),
    path('appapp/<int:id>/', views.delete_appointment_from_application, name='appapps-delete'),

    path('login/',  views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('reg/',  views.register, name='reg'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)