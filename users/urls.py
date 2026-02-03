from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    # User profile
    path('profile/', views.user_profile, name='user-profile'),

    # Utility
    path('check-email/', views.check_email, name='check-email'),
]