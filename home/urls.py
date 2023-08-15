from django.contrib import admin
from django.urls import path
from .views import home_page,busyness_page

urlpatterns = [
    path('',home_page,name="home"),
    path('busyness',busyness_page,name="busyness")
   
]
