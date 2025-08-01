# Users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import CustomUser

def login_view(request):
    """
    Handles the user login process.
    - For a GET request, it displays an empty login form.
    - For a POST request, it validates the submitted form data. If the credentials
      are correct, it logs the user in and redirects them to their profile page.
      If the credentials are not valid, it displays the form again with an error message.
    """
    message = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # If authentication is successful, log the user in
            login(request, user)
            
            # Update login time
            user.login_time = timezone.now()
            user.on_duty = True  # Set user as on duty when they log in
            user.save()
            
            return redirect('profile')  # Redirect to the profile page after login
        else:
            # If authentication fails, show an error message
            message = "Invalid username or password."
    
    # The context dictionary passes data to the template
    context = {'message': message}
    # Renders the login.html template with the form and any messages
    return render(request, 'users/login.html', context)


@login_required
def logout_view(request):
    """
    Handles the user logout process.
    This view logs out the current user and redirects them to the login page.
    """
    if request.user.is_authenticated:
        # Update logout time and duty status
        user = request.user
        user.logout_time = timezone.now()
        user.on_duty = False  # Set user as off duty when they log out
        user.save()
    
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    """
    Displays the profile page for the currently logged-in user.
    The @login_required decorator ensures that this page is only accessible
    to users who are logged in. It fetches the user object from the request
    and passes it to the template.
    """
    # The 'request.user' object is automatically available for logged-in users.
    # It contains all the information from our CustomUser model.
    user = request.user
    
    # Get recent asset activity for this user
    recent_asset_logs = None
    try:
        # Import here to avoid circular imports
        from assets.models import AssetLog
        recent_asset_logs = AssetLog.objects.filter(
            user=user
        ).select_related('asset').order_by('-timestamp')[:10]
    except ImportError:
        # Assets app might not be available
        pass
    
    context = {
        'user': user,
        'recent_asset_logs': recent_asset_logs,
    }
    return render(request, 'users/profile.html', context)


