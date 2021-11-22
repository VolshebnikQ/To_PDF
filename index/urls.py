from django.urls import path
from . import views
from .views import *


urlpatterns = [
    path('', views.Index.as_view(), name='index'),
]
