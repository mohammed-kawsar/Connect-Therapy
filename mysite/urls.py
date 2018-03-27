from django.urls import path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import password_reset, password_reset_complete, password_reset_done, \
    password_reset_confirm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('connect_therapy.urls.urls')),
    path('password_reset/',
         password_reset,
         {'template_name': 'connect_therapy/password_reset_form.html'},
         name='password_reset'
         ),
    path('password_reset/done/',
         password_reset_done, {'template_name': 'connect_therapy/password_reset_done.html'},
         name='password_reset_done'
         ),
    path('reset/<uidb64>/<token>/',
         password_reset_confirm, {'template_name': 'connect_therapy/password_reset_confirm.html'},
         name='password_reset_confirm'
         ),
    path('reset/done/',
         password_reset_complete, {'template_name': 'connect_therapy/password_reset_complete.html'},
         name='password_reset_complete'
         ),
]
