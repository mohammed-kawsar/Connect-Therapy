from django.urls import path, reverse_lazy, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.urls import re_path

from connect_therapy.views.views import *

app_name = 'connect_therapy'
urlpatterns = [
    path('patient/', include('connect_therapy.urls.patient')),
    path('practitioner/', include('connect_therapy.urls.practitioner')),
    path('chat/<int:pk>',
         ChatView.as_view(),
         name="chat"
         ),
    path('about',
         TemplateView.as_view(
             template_name='connect_therapy/about.html'
         ),
         name='about'),
    path('',
         TemplateView.as_view(
             template_name='connect_therapy/index.html'
         ),
         name='index'
         ),
    re_path(r'^reset-password/$',
            auth_views.password_reset,
            # {'post_reset_redirect': 'reset-password/done'},
            # 'template_name':'connect_therapy/password_reset_form.html',
            name='password_reset'
            ),
    re_path(r'^reset-password/done',
            auth_views.password_reset_done,
            name='password_reset_done'
            ),
    re_path(r'^reset-password/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
            auth_views.password_reset_confirm,
            # {'post_reset_redirect': 'reset-password/complete'},
            name='password_reset_confirm'
            ),
    re_path(r'^reset-password/complete/$',
            auth_views.password_reset_complete,
            name='password_reset_complete'
            ),
]
