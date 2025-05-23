from django.test import TestCase,Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from ci_cd.models import Module, Exercise, Repository, Enrollment, Progress

User = get_user_model()

class AuthTests(TestCase):

    def test_user_signup(self):
        response = self.client.post(reverse('signup'), {
            'username': 'testuser',
            'email': 'test@test.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_user_login(self):
        User.objects.create_user(username='testuser', password='12345678')
        login = self.client.login(username='testuser', password='12345678')
        self.assertTrue(login)

class DashboardTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='12345678')
        self.client.login(username='tester', password='12345678')

    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')

    def test_exercises_display(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your Progress')  # תוקן לפי מה שמופיע בפועל

class RepositoryTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='repo_creator', password='12345678')
        self.client.login(username='repo_creator', password='12345678')

    def test_create_repository(self):
        response = self.client.post(reverse('create_repository'), {
            'name': 'New Repo',
            'url': 'https://github.com/YazanW1/test-repo'
        })
        self.assertIn(response.status_code, [200, 302])


class RepositoryDisplayTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='display_user', password='12345678')
        self.client.login(username='display_user', password='12345678')

    def test_repository_appears_in_dashboard(self):
        # יצירת ריפוזיטורי ידנית
        from .models import Repository
        Repository.objects.create(name='repo-dashboard-test', user=self.user, url='https://github.com/testuser/testrepo')

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'repo-dashboard-test')  # מחפש את השם של הריפוזיטורי בדף

class ProgressBarTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='progress_user', password='12345678')
        self.client.login(username='progress_user', password='12345678')

    def test_progress_bar_display(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your Progress')  # טקסט שמייצג את אזור ההתקדמות


# === Sprint 2 User Story Tests ===


# User Story 2: Start guided CI/CD exercise
class GuidedExerciseTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='student1', password='pass')
        self.client.login(username='student1', password='pass')

    def test_ci_cd_intro_view(self):
        response = self.client.get(reverse('ci_cd_intro'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Introduction to CI/CD")


# User Story 3: Create and manage courses
class ModuleTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='inst1', password='pass', is_instructor=True)
        self.client.login(username='inst1', password='pass')

    def test_create_module(self):
        response = self.client.post(reverse('create_module'), {
            'title': 'Test Module',
            'description': 'Test description'
        })
        self.assertEqual(response.status_code, 302)

# User Story 4: Assign exercises
class ExerciseTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='inst2', password='pass', is_instructor=True)
        self.module = Module.objects.create(title='Test Mod', description='desc')
        self.client.login(username='inst2', password='pass')

    def test_create_exercise(self):
        response = self.client.post(reverse('create_exercise', args=[self.module.id]), {
            'title': 'Exercise A',
            'description': 'Do it',
            'difficulty': 3,  # or whatever choices you use
            'steps': '1. Clone the repo\n2. Run tests\n3. Deploy',
            'solution': 'print("solution")'
        })
        self.assertEqual(response.status_code, 302)

# User Story 5: Push code to GitHub
class GitPushTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='student2', password='pass')
        self.repo = Repository.objects.create(name="RepoPush", user=self.user)
        self.client.login(username='student2', password='pass')

    def test_commit_and_push(self):
        # Adjusted to prevent view fallback
        response = self.client.post(reverse('commit_and_push', args=[self.repo.id]), {
            'file_path': 'test.py',
            'content': 'print("Hello World")',
            'commit_message': 'Initial commit'
        })
        self.assertIn(response.status_code, [200, 302])


# User Stories 6 & 7: Run automated tests and trigger CI/CD
class RunTestsCI(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='student3', password='pass')
        self.repo = Repository.objects.create(name="TestRepo", user=self.user)
        self.client.login(username='student3', password='pass')

    def test_run_tests(self):
        response = self.client.get(reverse('run_tests', args=[self.repo.id]))
        self.assertEqual(response.status_code, 302)

# User Story 8: Docker basics learning page
class DockerBasicsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='student4', password='pass')
        self.client.login(username='student4', password='pass')

    def test_docker_basics_page(self):
        response = self.client.get(reverse('docker_basics'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Docker")

# User Story 10: Monitor student performance
class InstructorPerformanceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.instructor = User.objects.create_user(username='instructor1', password='pass', is_instructor=True)
        self.student = User.objects.create_user(username='student5', password='pass')
        self.module = Module.objects.create(title='Test Mod', description='desc')
        self.exercise = Exercise.objects.create(title='Ex1', description='test', module=self.module)
        self.client.login(username='instructor1', password='pass')

    def test_dashboard_includes_student_progress(self):
        Enrollment.objects.create(user=self.student, module=self.module)
        Progress.objects.create(user=self.student, exercise=self.exercise, completed=False)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.student.username)
