from django.urls import path
from . import views
from django.http import HttpResponse



def test_page(request):
    return HttpResponse("Yazan UwU!")

def yazan(request):
    return HttpResponse("Hodaaiiifaaaaaa UwU!")



urlpatterns = [
    path('', views.home, name='home'),  
    path('test/', views.test_view, name='test'),
    path("hello/", test_page, name="hello_page"),
    path("yazan/", yazan, name="yazan"),
     path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("enroll/<int:module_id>/", views.enroll_in_module, name="enroll"),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('intro/', views.ci_cd_intro, name='ci_cd_intro'),
    path('create-repo/', views.create_repository, name='create_repo'),
    path("module/<int:module_id>/", views.module_detail_view, name="module_detail"),
    path('exercise/<int:exercise_id>/complete/', views.mark_exercise_complete, name='mark_complete'),
    path("git-basics/", views.git_basics_view, name="git_basics"),
    path("cicd-logs/", views.cicd_logs_view, name="cicd_logs"),

]
