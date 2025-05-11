# models.py
from django.contrib.auth.models import User
from django.db import models

class Stock(models.Model):
    ticker = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    portfolio = models.ManyToManyField(Stock, related_name='portfolio_users', blank=True)
    watchlist = models.ManyToManyField(Stock, related_name='watchlist_users', blank=True)
