from django.urls import path
from . import views

urlpatterns = [
    path('<str:symbol>/details/', views.stock_details, name='stock_details'),
    path('<str:symbol>/search/', views.stock_lookup, name='stock_lookup'),
    path('<str:symbol>/chart/', views.get_stock_chart, name="stock_chart"),
    path('home/', views.home_stocks, name="home_stocks"),
    path('<str:symbol>/analysis/', views.stock_analysis, name='stock_analysis'),
    path('index/', views.index_data, name='market_index')
]
