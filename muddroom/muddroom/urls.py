from django.urls import path
from . import views

urlpatterns = [
    path('', views.hub, name='hub'),
    path('webhooks/receive/', views.webhook_receiver, name='webhook_receive')
]