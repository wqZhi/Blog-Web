"""
URL configuration for webapps project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

"""
URL configuration for webapps project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from socialnetwork import views

urlpatterns = [
    path('', views.index_action, name='home'),
    path('login/', views.login_action, name='login'),
    path('logout/', views.logout_action, name='logout'),
    path('register/', views.register_action, name='register'),
    path('globalStream/', views.global_stream_action, name='globalStream'),
    path('followerStream/', views.follower_stream_action, name='followerStream'),
    path('myProfile/', views.my_profile_action, name='myProfile'),
    path('profile/<str:username>/', views.other_profile_action, name='other_profile'),
    path('photo/<int:id>/', views.get_photo, name='photo'),
    path('follow/<str:username>/', views.follow_action, name='follow'),
    path('unfollow/<str:username>/', views.unfollow_action, name='unfollow'),
    
    # path('add-comment', views.add_comment, name='add_comment'),
    path('socialnetwork/get-global', views.get_global, name='get_global'),
    path('socialnetwork/get-follower', views.get_follower, name='get_follower'), 
    path('socialnetwork/add-comment', views.add_comment, name='add_comment'),
    path('socialnetwork/add-post', views.add_post, name='add_post'),
]