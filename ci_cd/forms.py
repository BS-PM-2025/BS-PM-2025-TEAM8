from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User , Repository,Profile,Module,Exercise
from django.contrib.auth import get_user_model
import re
from django.forms import ModelForm



User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    is_instructor = forms.BooleanField(required=False, label="Sign up as instructor")  # Add the checkbox

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "is_instructor"]  # Include the new field

        

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))        


class RepositoryForm(forms.ModelForm):
    class Meta:
        model = Repository
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data['name']
        if not re.match(r'^[a-zA-Z0-9-_]+$', name):
            raise forms.ValidationError("Repository name can only contain letters, numbers, dashes (-), and underscores (_).")
        return name    



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['is_instructor']


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description']


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['title', 'description', 'difficulty', 'steps', 'resources', 'solution']


class CodePushForm(forms.Form):
    filename = forms.CharField(max_length=255, label="Filename")
    file_content = forms.CharField(widget=forms.Textarea, label="File Content")
    commit_message = forms.CharField(max_length=255, label="Commit Message")

class TestFileForm(forms.Form):
    filename = forms.CharField(max_length=255, label="Filename")
    content = forms.CharField(widget=forms.Textarea, label="File Content")


class EditProfileForm(ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    class Meta:
        model = Profile
        fields = ['notifications_enabled']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(EditProfileForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['email'].initial = user.email
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

    def save(self, commit=True, user=None):
        profile = super(EditProfileForm, self).save(commit=False)
        if user:
            user.email = self.cleaned_data['email']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            if commit:
                user.save()
        if commit:
            profile.save()
        return profile
    

