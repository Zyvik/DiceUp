from django.urls import path
from . import views

app_name = 'DiceUp'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('example', views.example, name='example')
]
