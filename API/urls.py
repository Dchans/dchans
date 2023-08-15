from django.contrib import admin
from django.urls import path
from .views import user_register,user_login,backup_data,user_info,download_database

urlpatterns = [
    path('api/register',user_register.as_view(),name="register_api"),
    path('api/login',user_login.as_view(),name="login_api"),
    #path('api/generate_otp',generate_otp.as_view(),name="otp_api"),
    #path('api/verify',otp_verify.as_view(),name="verify_api"),
    path('api/backup',backup_data.as_view(),name="backup_api"),
    path('api/userinfo',user_info.as_view(),name="userinfo_api"),
    path('api/download_db',download_database.as_view(),name="db_api"),
]
