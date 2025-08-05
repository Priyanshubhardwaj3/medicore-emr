from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('emr_app.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='emr_app/login.html'), name='login'),
]
