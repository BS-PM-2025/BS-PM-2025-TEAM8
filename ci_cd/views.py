from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm, LoginForm ,RepositoryForm
from django.contrib.auth.decorators import login_required
from .models import Module, Enrollment , Repository ,Progress , Exercise
from django.contrib import messages
from django.contrib.auth import get_user_model
import requests

# Get the User model
User = get_user_model()

# User Signup
def signup_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user

            # Set the is_instructor field for the user
            user.is_instructor = form.cleaned_data['is_instructor']
            user.save()

            login(request, user)  # Log the user in after registration
            return redirect("dashboard")
        else:
            messages.error(request, "There was an error with your submission.")
            print("❌ Registration form errors:", form.errors)  # Debugging
    else:
        form = UserRegistrationForm()
    return render(request, "ci_cd/signup.html", {"form": form})

# User Login
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            print(f"🔍 Trying to authenticate: {username}")  # Debugging

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                print(f"✅ {username} logged in successfully!")  # Debugging
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid username or password")
                print("❌ Authentication failed!")  # Debugging
    else:
        form = LoginForm()
    return render(request, "ci_cd/login.html", {"form": form})

# User Logout
def logout_view(request):
    logout(request)
    print("🚪 User logged out successfully")  # Debugging
    return redirect("login")

# Home Page
def home(request):
    return HttpResponse("Hello, this is the home page!")

# Test Page
def test_view(request):
    return HttpResponse("This is the test page!")

# Enroll in Module
@login_required
def enroll_in_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    enrollment, created = Enrollment.objects.get_or_create(user=request.user, module=module)

    if created:
        message = f"✅ Successfully enrolled in {module.title}!"
        print(message)  # Debugging
    else:
        message = f"⚠️ You are already enrolled in {module.title}."
        print(message)  # Debugging

    return render(request, "ci_cd/enroll_success.html", {"message": message})

# Dashboard Page
@login_required
def dashboard_view(request):
    repositories = Repository.objects.filter(user=request.user)
    if request.user.is_instructor:
        # Instructor Dashboard
        students = User.objects.filter(is_instructor=False)  # Get all students
        progress_data = {}

        for student in students:
            progress = Progress.objects.filter(user=student)
            completed = progress.filter(completed=True).count()
            total_exercises = progress.count()
            progress_percent = int((completed / total_exercises) * 100) if total_exercises else 0
            progress_data[student] = {
                "completed": completed,
                "total_exercises": total_exercises,
                "progress_percent": progress_percent
            }

        return render(request, "ci_cd/instructor_dashboard.html", {
            "students": progress_data
        })
    else:
        # Student Dashboard
        enrolled_modules = Module.objects.filter(enrollment__user=request.user)
        available_modules = Module.objects.exclude(id__in=[module.id for module in enrolled_modules])

        # Get the progress details for the enrolled modules
        total_exercises = Exercise.objects.filter(module__in=enrolled_modules).count()
        completed = Progress.objects.filter(user=request.user, completed=True, exercise__module__in=enrolled_modules).count()

        progress_percent = int((completed / total_exercises) * 100) if total_exercises else 0

        return render(request, "ci_cd/dashboard.html", {
            "repositories": repositories,
            "enrolled_modules": enrolled_modules,
            "available_modules": available_modules,
            "completed": completed,
            "total_exercises": total_exercises,
            "progress_percent": progress_percent,
            "message": "Welcome, Student!"
        })



@login_required
def ci_cd_intro(request):
    return render(request, "ci_cd/ci_cd_intro.html")

def create_repository(request):
    if request.method == 'POST':
        form = RepositoryForm(request.POST)
        if form.is_valid():
            repo = form.save(commit=False)
            repo.user = request.user
            repo.save()
            return redirect('dashboard')  # or a separate page like 'my_repos'
    else:
        form = RepositoryForm()

    return render(request, 'ci_cd/create_repository.html', {'form': form})


@login_required
def module_detail_view(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    return render(request, "ci_cd/module_detail.html", {"module": module})



@login_required
def module_detail_view(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    exercises = module.exercises.all()
    completed_ids = Progress.objects.filter(user=request.user, completed=True, exercise__in=exercises).values_list("exercise_id", flat=True)

    return render(request, "ci_cd/module_detail.html", {
        "module": module,
        "exercises": exercises,
        "completed_ids": completed_ids,
    })


@login_required
def mark_exercise_complete(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id)

    # Create a Progress object if it doesn't exist
    progress, created = Progress.objects.get_or_create(
        user=request.user,
        exercise=exercise,
        defaults={"completed": True}
    )

    # If it already exists and not marked complete, update it
    if not created and not progress.completed:
        progress.completed = True
        progress.save()

    return redirect("module_detail", module_id=exercise.module.id)


@login_required
def git_basics_view(request):
    return render(request, "ci_cd/git_basics.html")




@login_required
def create_repository_view(request):
    if request.method == "POST":
        form = RepositoryForm(request.POST)
        if form.is_valid():
            repo = form.save(commit=False)
            repo.user = request.user
            repo.save()

            # ✅ Print GitHub repo debug info
            print(f"🚀 New repository created: {repo.name} | {repo.url}")

            github_url = repo.url
            api_url = github_url.replace("https://github.com/", "https://api.github.com/repos/")
            print(f"🔗 Checking GitHub API: {api_url}")

            try:
                response = requests.get(api_url)
                print(f"📡 GitHub response status: {response.status_code}")

                if response.status_code == 200:
                    repo_info = response.json()
                    is_private = repo_info.get("private", False)
                    has_files = repo_info.get("size", 0) > 0

                    print("✅ Repo exists on GitHub!")
                    print(f"🔒 Private: {is_private}")
                    print(f"📁 Has files: {has_files}")

                    messages.success(request, "✅ Repository found and verified on GitHub!")
                else:
                    print("❌ GitHub repo not found or not accessible.")
                    messages.warning(request, "⚠️ GitHub repo not found or is private.")
            except Exception as e:
                print("🔥 Error checking GitHub repo:", e)
                messages.error(request, "An error occurred while validating the GitHub repo.")

            return redirect("dashboard")
    else:
        form = RepositoryForm()
    
    return render(request, "ci_cd/create_repository.html", {"form": form})

@login_required
def cicd_logs_view(request):
    return render(request, "ci_cd/cicd_logs.html")

def test_message(request):
    messages.success(request, "🎉 This is a test success message!")
    messages.warning(request, "⚠️ This is a test warning!")
    messages.error(request, "❌ This is a test error!")
    return redirect("dashboard")

@login_required
def create_module(request):
    if request.user.is_instructor:  # Check if the user is an instructor
        if request.method == "POST":
            form = ModuleForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('dashboard')  # Redirect after creating the module
        else:
            form = ModuleForm()

        return render(request, "ci_cd/create_module.html", {'form': form})

    return redirect("dashboard")  # Redirect if the user is not an instructor

