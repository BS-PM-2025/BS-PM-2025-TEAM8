from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

# Custom User Model
class User(AbstractUser):
    is_instructor = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, related_name="ci_cd_users")
    user_permissions = models.ManyToManyField(Permission, related_name="ci_cd_users_permissions")

    def __str__(self):
        return self.username

# CI/CD Learning Modules
class Module(models.Model):
    title = models.CharField(max_length=200, unique=True)  # Ensures no duplicate titles
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]  # Show newest modules first

    def __str__(self):
        return self.title

class Exercise(models.Model):
    DIFFICULTY_LEVELS = [(i, f"Level {i}") for i in range(1, 6)]  # Choices for difficulty (1-5)

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="exercises")
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.IntegerField(choices=DIFFICULTY_LEVELS, default=1)
    steps = models.TextField(help_text="Detailed steps to complete this task")
    resources = models.TextField(help_text="External resources (URLs) for reference", blank=True, null=True)
    solution = models.TextField(help_text="Detailed solution for instructors (optional)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["difficulty", "created_at"]

    def __str__(self):
        return f"{self.title} (Module: {self.module.title})"
    


class Quiz(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=[
        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')
    ])

    def __str__(self):
        return self.question_text




# Tracking Student Progress
class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, null=True, blank=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True)
    completed = models.BooleanField(default=False)
    score = models.IntegerField(null=True, blank=True)
    quiz_score = models.IntegerField(null=True, blank=True)


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



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_instructor = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    notifications_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"To {self.receiver.username}: {self.message[:30]}"


class Review(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, f"{i} Stars") for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.module.title} ({self.rating}★)"
