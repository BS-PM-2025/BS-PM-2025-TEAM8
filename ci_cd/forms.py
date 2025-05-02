from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User , Repository
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))        


class RepositoryForm(forms.ModelForm):
    class Meta:
        model = Repository
        fields = ['name', 'url']

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['is_instructor']
