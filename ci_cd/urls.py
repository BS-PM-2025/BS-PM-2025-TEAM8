from django.urls import path
from . import views
from django.http import HttpResponse



def test_page(request):
    return HttpResponse("Yazan UwU!")

def yazan(request):
    return HttpResponse("Hodaaiiifaaaaaa UwU!")



urlpatterns = [
    path('', views.login_view, name='home'),  
    path('test/', views.test_view, name='test'),
    path("hello/", test_page, name="hello_page"),
    path("yazan/", yazan, name="yazan"),
     path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path('enroll/<int:module_id>/', views.enroll_in_module, name='enroll_in_module'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('intro/', views.ci_cd_intro, name='ci_cd_intro'),
    path('create_repository/', views.create_repository, name='create_repository'),
    path("module/<int:module_id>/", views.module_detail_view, name="module_detail"),
    path('exercise/<int:exercise_id>/complete/', views.mark_exercise_complete, name='mark_complete'),
    path("git-basics/", views.git_basics_view, name="git_basics"),
    path("cicd-logs/", views.cicd_logs_view, name="cicd_logs"),
    path("test-message/", views.test_message),
    path('create-module/', views.create_module, name='create_module'),
    path('create_exercise/<int:module_id>/', views.create_exercise, name='create_exercise'),
    path("commit_and_push/<int:repo_id>/", views.commit_and_push, name="commit_and_push"),
    path("add_test_file/<int:repo_id>/", views.add_test_file, name="add_test_file"),
    path("run_tests/<int:repo_id>/", views.run_tests, name="run_tests"),
    path("docker/", views.docker_basics_view, name="docker_basics"),

]
