# Users/urls.py

from django.urls import path
from . import views

# This is a list of URL patterns for the Users application.
# Each path maps a URL route to a specific view function from views.py.
# The 'name' argument provides a unique identifier for each URL pattern,
# which is a best practice and allows us to easily refer to these URLs
# from other parts of the application, such as in templates or redirects.

urlpatterns = [
    # URL for the login page.
    # When a user navigates to '/users/login/', Django will call the login_view function.
    # We've named this URL pattern 'login'.
    path('login/', views.login_view, name='login'),

    # URL for the logout functionality.
    # Navigating to '/users/logout/' will call the logout_view function.
    # We've named this 'logout'.
    path('logout/', views.logout_view, name='logout'),

    # URL for the user profile page.
    # Navigating to '/users/profile/' will call the profile_view function.
    # We've named this 'profile'.
    path('profile/', views.profile_view, name='profile'),
]
