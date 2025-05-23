import os
from django.conf import settings
from git import Repo,GitCommandError
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm, LoginForm ,RepositoryForm,ModuleForm,ExerciseForm,CodePushForm,TestFileForm,EditProfileForm,NotificationForm
from django.contrib.auth.decorators import login_required
from .models import Module, Enrollment , Repository ,Progress , Exercise ,Profile,Module,Notification
from django.contrib import messages
from django.contrib.auth import get_user_model
import requests
import base64
import subprocess
import shutil




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
        # Automatically create Progress records for each exercise
        exercises = Exercise.objects.filter(module=module)  # Fetch real CI/CD exercises
        for exercise in exercises:
            Progress.objects.get_or_create(user=request.user, exercise=exercise)

        message = f"✅ Successfully enrolled in {module.title}!"
        print(message)  # Debugging
    else:
        message = f"⚠️ You are already enrolled in {module.title}."
        print(message)  # Debugging

    return render(request, "ci_cd/enroll_success.html", {"message": message})


@login_required
def dashboard_view(request):
    if request.user.is_instructor:
        # Instructor Dashboard
        modules = Module.objects.all()
        students = User.objects.filter(is_instructor=False)
        notifications = Notification.objects.filter(receiver=request.user, read=False)
        progress_data = {}

        for student in students:
            progress = Progress.objects.filter(user=student)
            total_exercises = Exercise.objects.filter(module__in=Module.objects.filter(enrollment__user=student)).count()
            completed = progress.filter(completed=True).count()
            progress_percent = int((completed / total_exercises) * 100) if total_exercises else 0

            if total_exercises == 0:
                needs_help = False
            else:
                needs_help = progress_percent < 50

            progress_data[student] = {
                "completed": completed,
                "total_exercises": total_exercises,
                "progress_percent": progress_percent,
                "needs_help": needs_help
            }

        return render(request, "ci_cd/instructor_dashboard.html", {
            "modules": modules,
            "students": progress_data,
            "notifications": notifications
        })

    else:
        # Student Dashboard (unchanged)
        enrolled_modules = Module.objects.filter(enrollment__user=request.user)
        available_modules = Module.objects.exclude(id__in=[module.id for module in enrolled_modules])
        total_exercises = Exercise.objects.filter(module__in=enrolled_modules).count()
        completed = Progress.objects.filter(user=request.user, completed=True, exercise__module__in=enrolled_modules).count()
        progress_percent = int((completed / total_exercises) * 100) if total_exercises else 0

        return render(request, "ci_cd/dashboard.html", {
            "repositories": Repository.objects.filter(user=request.user),
            "enrolled_modules": enrolled_modules,
            "available_modules": available_modules,
            "completed": completed,
            "total_exercises": total_exercises,
            "progress_percent": progress_percent
        })



@login_required
def ci_cd_intro(request):
    return render(request, "ci_cd/ci_cd_intro.html")


#GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "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")


@login_required
def create_repository(request):
    if request.method == "POST":
        form = RepositoryForm(request.POST)
        if form.is_valid():
            repo = form.save(commit=False)
            repo.user = request.user

            repo_name = repo.name
            owner = "YazanW1"  # Your GitHub username

            # GitHub API request to create the repo
            api_url = "https://api.github.com/user/repos"
            headers = {
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }

            data = {
                "name": repo_name,
                "description": f"Repository for {repo_name}",
                "private": False
            }

            response = requests.post(api_url, json=data, headers=headers)

            if response.status_code == 201:
                # Save repo URL
                repo.url = f"https://github.com/{owner}/{repo_name}.git"
                repo.save()

                # Clone locally
                repo_path = os.path.join(settings.BASE_DIR, "repos", str(repo.id))

                # ✅ Fix: Clean the folder if it already exists and is not empty
                if os.path.exists(repo_path) and os.listdir(repo_path):
                    shutil.rmtree(repo_path)

                os.makedirs(repo_path, exist_ok=True)
                Repo.clone_from(repo.url, repo_path)


                # Inject token for push access
                repo_git = Repo(repo_path)
                remote_with_token = f"https://{GITHUB_TOKEN}:x-oauth-basic@github.com/{owner}/{repo_name}.git"
                repo_git.remotes.origin.set_url(remote_with_token)

                # Create tests/ directory
                tests_dir = os.path.join(repo_path, "tests")
                os.makedirs(tests_dir, exist_ok=True)
                with open(os.path.join(tests_dir, ".gitkeep"), "w") as f:
                    f.write("")

                # Create Dockerfile
                dockerfile_content = """
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install pytest
CMD ["pytest", "tests"]
""".strip()

                with open(os.path.join(repo_path, "Dockerfile"), "w") as dockerfile:
                    dockerfile.write(dockerfile_content)

                # Commit and push everything
                repo_git.git.add(all=True)
                repo_git.index.commit("Initialize with tests/ directory and Dockerfile")
                repo_git.remotes.origin.push()

                messages.success(request, f"🚀 Repository created and pushed at {repo.url}")
                return redirect("dashboard")
            else:
                error_message = response.json().get("message", "Unknown error")
                messages.error(request, f"❌ Error creating repo: {error_message}")
    else:
        form = RepositoryForm()

    return render(request, "ci_cd/create_repository.html", {"form": form})





def create_tests_directory(owner, repo_name, headers):
    """Create a tests/ directory in the new repository"""
    url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/tests/.gitkeep"
    data = {
        "message": "Create tests directory",
        "content": "",
        "branch": "main"
    }
    response = requests.put(url, json=data, headers=headers)

    if response.status_code == 201 or response.status_code == 200:
        print(f"✅ Created tests/ directory in {repo_name}")
    else:
        print(f"❌ Failed to create tests/ directory in {repo_name}: {response.json()}")








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


@login_required
def create_exercise(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if request.method == "POST":
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.module = module  # Assign the exercise to the specific module
            exercise.save()
            print(f"✅ New exercise created for module {module.title}: {exercise.title}")
            return redirect('module_detail', module_id=module.id)
        else:
            print("❌ Form is not valid:", form.errors)
    else:
        form = ExerciseForm()

    return render(request, "ci_cd/create_exercise.html", {"form": form, "module": module})



@login_required
def commit_and_push(request, repo_id):
    try:
        repo = Repository.objects.get(id=repo_id, user=request.user)

        if request.method == "POST":
            form = CodePushForm(request.POST)
            if form.is_valid():
                filename = form.cleaned_data["filename"]
                commit_message = form.cleaned_data["commit_message"]
                file_content = form.cleaned_data["file_content"]

                # Extract the owner and repository name from the URL
                url_parts = repo.url.replace("https://github.com/", "").split("/")
                owner = url_parts[0]
                repo_name = url_parts[1].replace(".git", "")

                # Encode the file content to Base64
                encoded_content = base64.b64encode(file_content.encode("utf-8")).decode("utf-8")

                # Check if the file already exists
                check_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{filename}"
                headers = {
                    "Authorization": f"Bearer {GITHUB_TOKEN}",
                    "Accept": "application/vnd.github.v3+json"
                }

                response = requests.get(check_url, headers=headers)

                # Prepare the data for the push
                data = {
                    "message": commit_message,
                    "content": encoded_content,
                    "branch": "main"  # Use "master" if that's the default branch
                }

                # If the file already exists, add the SHA
                if response.status_code == 200:
                    file_info = response.json()
                    data["sha"] = file_info["sha"]

                # Push the file
                push_response = requests.put(check_url, json=data, headers=headers)

                if push_response.status_code == 201 or push_response.status_code == 200:
                    messages.success(request, "Code pushed successfully!")
                else:
                    error_message = push_response.json().get("message", "Unknown error")
                    messages.error(request, f"Error while pushing to GitHub: {error_message}")

                return redirect("dashboard")
        else:
            form = CodePushForm()

        return render(request, "ci_cd/commit_and_push.html", {"form": form, "repo": repo})

    except Repository.DoesNotExist:
        messages.error(request, "Repository not found or you don't have access to it.")
        return redirect("dashboard")




@login_required
def add_test_file(request, repo_id):
    try:
        repo = Repository.objects.get(id=repo_id, user=request.user)

        if request.method == "POST":
            form = TestFileForm(request.POST)
            if form.is_valid():
                filename = form.cleaned_data["filename"]
                content = form.cleaned_data["content"]

                # File path inside the repo
                file_path = f"tests/{filename}.py"

                # GitHub repo info
                url_parts = repo.url.replace("https://github.com/", "").split("/")
                owner = url_parts[0]
                repo_name = url_parts[1].replace(".git", "")

                # Upload via GitHub API
                url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{file_path}"
                headers = {
                    "Authorization": f"Bearer {GITHUB_TOKEN}",
                    "Accept": "application/vnd.github.v3+json"
                }
                data = {
                    "message": f"Add test file {filename}.py",
                    "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
                    "branch": "main"
                }

                response = requests.put(url, json=data, headers=headers)

                if response.status_code in [200, 201]:
                    messages.success(request, f"✅ Test file '{filename}.py' added to GitHub.")

                    # 🔄 Pull the update into the local clone
                    repo_path = os.path.join(settings.BASE_DIR, 'repos', str(repo.id))
                    try:
                        local_repo = Repo(repo_path)
                        local_repo.remotes.origin.pull()
                        messages.success(request, f"🔄 Local repository updated successfully.")
                    except Exception as e:
                        messages.warning(request, f"⚠️ Test uploaded, but failed to pull locally: {e}")
                else:
                    error_message = response.json().get("message", "Unknown error")
                    messages.error(request, f"❌ Error while adding test file: {error_message}")

                return redirect("dashboard")
        else:
            form = TestFileForm()

        return render(request, "ci_cd/add_test_file.html", {"form": form, "repo": repo})

    except Repository.DoesNotExist:
        messages.error(request, "❌ Repository not found or you don't have access.")
        return redirect("dashboard")





@login_required
def run_tests(request, repo_id):
    try:
        # Get the repository
        repo = Repository.objects.get(id=repo_id, user=request.user)

        # Define the local path to the tests directory
        repo_path = os.path.join(settings.BASE_DIR, 'repos', str(repo.id), 'tests')

        # Run the tests (force discovery)
        result = subprocess.run(
            [os.path.join(settings.BASE_DIR, 'venv', 'Scripts', 'python.exe'), "-m", "pytest", repo_path, "--verbose", "--doctest-modules", "--maxfail=3"],
            capture_output=True,
            text=True
        )

        # Capture the test output
        output = result.stdout if result.stdout else result.stderr

        # Show the test results as a message
        messages.info(request, output, extra_tags="test-result")
        return redirect("dashboard")

    except Repository.DoesNotExist:
        messages.error(request, "Repository not found or you don't have access to it.")
        return redirect("dashboard")
    except Exception as e:
        messages.error(request, f"Error while running tests: {e}")
        return redirect("dashboard")



@login_required
def docker_basics_view(request):
    return render(request, "ci_cd/docker_basics.html")


@login_required
def browse_modules(request):
    enrolled_ids = Enrollment.objects.filter(user=request.user).values_list("module_id", flat=True)
    modules = Module.objects.exclude(id__in=enrolled_ids)
    return render(request, "ci_cd/browse_modules.html", {"modules": modules})


@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user.profile, user=request.user)
        if form.is_valid():
            form.save(user=request.user)
            return redirect('dashboard')  # Or any success page
    else:
        form = EditProfileForm(instance=profile, user=request.user)

    return render(request, 'ci_cd/edit_profile.html', {'form': form})

@login_required
def view_profile(request):
    profile = request.user.profile
    return render(request, "ci_cd/view_profile.html", {"profile": profile})

@login_required
def send_notification(request):
    if not request.user.is_instructor:
        return redirect('dashboard')  # Restrict access to instructors only

    if request.method == "POST":
        form = NotificationForm(request.POST)
        if form.is_valid():
            notif = form.save(commit=False)
            notif.sender = request.user
            notif.save()
            return redirect('dashboard')
    else:
        form = NotificationForm()

    return render(request, "ci_cd/send_notification.html", {"form": form})

@login_required
def student_notifications(request):
    notifications = Notification.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, 'ci_cd/student_notifications.html', {
        'notifications': notifications
    })
