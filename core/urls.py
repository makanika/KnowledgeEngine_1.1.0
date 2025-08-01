# Core/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # The URL for the Django admin interface.
    path('admin/', admin.site.urls),

    # This is the most important line for our app.
    # It tells Django that any URL starting with 'users/' should be
    # handled by the urls.py file inside our 'Users' app.
    path('users/', include('users.urls')),
    
    # Assets application URLs
    # Any URL starting with 'assets/' will be handled by the assets app
    path('assets/', include('assets.urls')),

    # For user convenience, this line redirects the root URL of the site ('/')
    # directly to our login page ('/users/login/'). So, when someone visits
    # your website's homepage, they will be taken straight to the login form.
    path('', RedirectView.as_view(url='/users/login/', permanent=True)),
]

# This is a helper configuration that tells Django how to serve user-uploaded
# files (like profile photos) during development.
# This is not for production use; in a production environment, your web server
# (like Nginx or Apache) would be configured to handle this.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
