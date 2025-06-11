from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Module, Exercise, Progress

User = get_user_model()  # Get the user model dynamically

# Ensure the User model is registered only once
if not admin.site.is_registered(User):
    admin.site.register(User, UserAdmin)

admin.site.register(Module)
admin.site.register(Exercise)
admin.site.register(Progress)
