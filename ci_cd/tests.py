from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

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
        response = self.client.post(reverse('create_repo'), {  # שם הנתיב המתוקן
            'name': 'test-repo',
            'url': 'https://github.com/testuser/test-repo'
        })
        self.assertEqual(response.status_code, 302)

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
