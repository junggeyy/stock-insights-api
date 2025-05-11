from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Stock, UserProfile

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['ticker', 'name']

class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'password']

class UserProfileSerializer(serializers.ModelSerializer):
    portfolio = StockSerializer(many=True, read_only=True)
    watchlist = StockSerializer(many=True, read_only=True)
    avatar = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['avatar', 'name', 'portfolio', 'watchlist']

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None

    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"



