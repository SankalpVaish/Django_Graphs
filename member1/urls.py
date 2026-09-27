#This file contains the paths to different pages and which functions to be directed for page rendering. 

from django.urls import path, include
from . import views
from django.views.generic.base import TemplateView
from .views import SignUpView

urlpatterns = [
    # path('',  TemplateView.as_view(template_name='LandingPage.html'), name='LandingPage'),
    # path('home/', views.home, name='home'),
    path("accounts/", include("django.contrib.auth.urls")),
    path("signup/", SignUpView.as_view(), name="signup"),
    path('help/', views.contact, name='ContactUs'),
    path('about/', views.about, name='About'),
    path("preference/", views.user_preference, name="user_preference"),
    # path('MT/', views.ModelTraining, name='Model_Training'),
    # path('details/<int:id>/', views.house_details, name='house_details'),
    path('', views.LandingPage, name='LandingPage'),
    path('graph/', views.NextPage, name='GraphPage'),
    path('OutlierAnalysis/<name>', views.OutAnalysis, name='Outlier_Analysis'),
    path('ModelTraining/<str:model>/', views.ModelTraining, name='Model_Training'),
    path("ModelTraining/", views.ModelTrainingRoot, name="ModelTrainingRoot"),
    path("interactive-plots/", views.interactive_plots, name="interactive_plots"),

]