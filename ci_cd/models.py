from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

# Custom User Model
class User(AbstractUser):
    groups = models.ManyToManyField(Group, related_name="ci_cd_users")
    user_permissions = models.ManyToManyField(Permission, related_name="ci_cd_users_permissions")

    def __str__(self):
        return self.username

# CI/CD Learning Modules
class Module(models.Model):
    title = models.CharField(max_length=200, unique=True)  # Ensures no duplicate titles
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  # Show newest modules first

    def __str__(self):
        return self.title

# Hands-on Exercises
class Exercise(models.Model):
    DIFFICULTY_LEVELS = [(i, f"Level {i}") for i in range(1, 6)]  # Choices for difficulty (1-5)

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="exercises")
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.IntegerField(choices=DIFFICULTY_LEVELS, default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["difficulty", "created_at"]  # Sort by difficulty then by date

    def __str__(self):
        return f"{self.title} (Module: {self.module.title})"

# Tracking Student Progress
class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="progress")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="progress")
    completed = models.BooleanField(default=False)
    score = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "exercise")  # Prevents duplicate progress records
        ordering = ["-completed", "-score"]  # Sort completed first, then highest score

    def __str__(self):
        return f"{self.user.username} - {self.exercise.title} ({'Completed' if self.completed else 'In Progress'})"


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} enrolled in {self.module.title}"


class Repository(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

