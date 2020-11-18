from django.urls import path

from . import views

urlpatterns = [
    path('<int:movie_id>/',views.detail ,name='detail'),
    path('signup/',views.signUp,name='signup'),
    path('login/',views.Login,name='login'),
    path('logout/',views.Logout,name='logout'),
    path('recommend/',views.recommend,name='recommend'),
    path('profile', views.profile, name='profile'),
    path('home', views.home, name='home'),
    path('about', views.about, name='about')
]