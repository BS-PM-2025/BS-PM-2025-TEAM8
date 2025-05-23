from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User , Repository,Profile,Module,Exercise
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    is_instructor = forms.BooleanField(required=False, label="Sign up as instructor")
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "is_instructor"]
        

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

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['is_instructor']

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise

        fields = ['title', 'description', 'difficulty', 'steps', 'resources', 'solution']        
        
class TestFileForm(forms.Form):
    filename = forms.CharField(max_length=255, label="Filename")
    content = forms.CharField(widget=forms.Textarea, label="File Content")

class CodePushForm(forms.Form):
    filename = forms.CharField(max_length=255, label="Filename")
    file_content = forms.CharField(widget=forms.Textarea, label="File Content")
    commit_message = forms.CharField(max_length=255, label="Commit Message")

