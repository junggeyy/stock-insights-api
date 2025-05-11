# user/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('test_token/', views.test_token, name='test_token'),
    path('portfolio/add/', views.add_to_portfolio, name='add_to_portfolio'),
    path('watchlist/add/', views.add_to_watchlist, name='add_to_watchlist'),
    path('avatar/upload/', views.upload_avatar, name='upload_avatar'),
    path('portfolio/remove/', views.remove_from_portfolio, name='remove_from_portfolio'),
    path('watchlist/remove/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('portfolio/', views.portfolio_list, name='portfolio_list'),
    path('watchlist/', views.watchlist_list, name='watchlist_list'),
    path('watchlist/contains/<str:ticker>/', views.is_in_watchlist, name='is_in_watchlist'),
]
