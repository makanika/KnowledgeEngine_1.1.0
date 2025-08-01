# Users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm # We will create this form in the next step

def login_view(request):
    """
    Handles the user login process.
    - For a GET request, it displays an empty login form.
    - For a POST request, it validates the submitted form data. If the credentials
      are correct, it logs the user in and redirects them to their profile page.
      If the credentials are not valid, it displays the form again with an error message.
    """
    form = LoginForm()
    message = ''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                # Redirect to the user's profile page upon successful login
                return redirect('profile') 
            else:
                # This message will be displayed on the login page if authentication fails
                message = 'Invalid username or password'
    
    # The context dictionary passes data to the template
    context = {'form': form, 'message': message}
    # Renders the login.html template with the form and any messages
    return render(request, 'users/login.html', context)


@login_required
def logout_view(request):
    """
    Logs the current user out and redirects them to the login page.
    The @login_required decorator ensures that only authenticated users can access this view.
    """
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
    context = {'user': user}
    return render(request, 'users/profile.html', context)


