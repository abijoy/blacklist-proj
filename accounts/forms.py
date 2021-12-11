# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from allauth.account.forms import SignupForm
from django.contrib.auth import get_user_model
from django import forms
from allauth.account.forms import LoginForm, SignupForm



class MyCustomSignupForm(SignupForm):

    def __init__(self, *args, **kwargs):
        super(MyCustomSignupForm, self).__init__(*args, **kwargs)
    # recreating form fields
        self.fields['user_type'] = forms.ChoiceField(choices=[('lir', 'Local Internet Registrars'), ('personal', 'Personal')])
        self.fields['fullname'] = forms.CharField(label='Enter fullname',
                                widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'fullname', 'placeholder': 'Full Name'}))
        self.fields['email'] = forms.EmailField(label='Enter Email',
                                widget=forms.EmailInput(attrs={'class': 'form-control', 'name': 'email', 'placeholder': 'Email'}))
        self.fields['username'] = forms.CharField(label='Enter Username',
                                widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username', 'placeholder': 'Username'}))
        self.fields['password1'] = forms.CharField(label='Enter password', 
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'name': 'password', 'placeholder': 'Password'}))
        self.fields['password2'] = forms.CharField(label='Confirm password', 
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'name': 'confirm_password', 'placeholder': 'Confirm Password'}))
    
    def save(self, request):
        user = super(MyCustomSignupForm, self).save(request)
        user.fullname = self.cleaned_data['fullname']
        user.user_type = self.cleaned_data['user_type']
        user.save()
        return user


class MyCustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(MyCustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'] = forms.CharField(label='Enter Username',
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username', 'placeholder': 'Username'}))
                            
        self.fields['password'] = forms.CharField(label='Enter password', 
                                    widget=forms.PasswordInput(attrs={'class': 'form-control', 'name': 'password', 'placeholder': 'Password'}))
