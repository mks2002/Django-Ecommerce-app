from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,       
    AuthenticationForm,
    PasswordChangeForm,
    UsernameField,
    PasswordResetForm,
    SetPasswordForm,
)


from django.contrib.auth.models import User
from django.utils.translation import gettext, gettext_lazy as _
from .models import Customer
from django.contrib.auth import password_validation



# here we create our custom user registration form.......
class CustomerRegistrationForm(UserCreationForm):
    password1 = forms.CharField(
        label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirm Password (again)',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    email = forms.CharField(
        required=True, widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    # if we define label here it will more dominating......
    # email = forms.CharField(label='main email',
    #     required=True, widget=forms.EmailInput(attrs={'class': 'form-control'})
    # )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {'email': 'Email'}
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control'})}


# this is our custom loginform we use this so that we can modify this using bootstrap class........
class LoginForm(AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'})
    )
    password = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'current-password', 'class': 'form-control'}
        ),
    )
# So, if the code is used in a multilingual website or application, the password label can be easily translated to different languages by simply translating the corresponding strings in the translation files....  
# for using that we have to import ----->
# from django.utils.translation import gettext, gettext_lazy as _




# this is the custom password change form using the old password.......
class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=_('Old Password'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'current-password',
                'autofocus': True,
                'class': 'form-control',
            }
        ),
    )
    new_password1 = forms.CharField(
        label=_('New Password'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'form-control'}
        ),
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_('Confirm New Password'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'form-control'}
        ),
    )

# this view is for forgot password here use have to submit his email then a link for updating password is send to the email and then it is done.....
class MyPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        widget=forms.EmailInput(
            attrs={'autocomplete': 'email', 'class': 'form-control'}
        ),
    )

# after the link is generated from the previous form then this form is render to update the new password.......
class MySetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_('New Password'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'form-control'}
        ),
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_('Confirm New Password'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'form-control'}
        ),
    )



# this form is for saving the different customer data which is corresponding to one user of the website and this form is remder when the user is just logged in ......
# this is a complete model form here we dont use any default form of django....
class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'locality', 'city', 'state', 'zipcode']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'locality': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.Select(attrs={'class': 'form-control'}),
            'zipcode': forms.NumberInput(attrs={'class': 'form-control'}),
        }
