# Users/forms.py

from django import forms

class LoginForm(forms.Form):
    """
    This form is used for user authentication. It defines the fields
    that will be rendered in the HTML template for the login page.
    Django handles the rendering of the form fields, data validation,
    and cleaning of the submitted data.
    """
    # The username field. It's a standard character field.
    # We add a widget attribute to apply CSS classes that match your theme.
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter your username'
            }
        )
    )

    # The password field.
    # We use a PasswordInput widget to ensure the text is obscured in the browser.
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 mt-4',
                'placeholder': 'Enter your password'
            }
        )
    )

