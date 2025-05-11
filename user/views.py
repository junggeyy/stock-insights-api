from rest_framework.decorators import api_view  # handles http resquests in RESTful
from rest_framework.response import Response    # formats http response data in JSON

from .serializers import StockSerializer, UserProfileSerializer, UserSerializer # converts User model into JSON format for validation
from rest_framework import status   # provides set of constants to represent status codes
from rest_framework.authtoken.models import Token   # generate token for user for API-authentication
from django.contrib.auth.models import User     # django User model, builtin user management functionalities
from .models import UserProfile, Stock
from django.shortcuts import get_object_or_404

@api_view(['POST'])
def login(request):
    # find a User object with the email
    user = get_object_or_404(User, email=request.data['email'])
    if not user.check_password(request.data['password']):
        return Response({"detail": "Not found"}, status=status.HTTP_400_BAD_REQUEST)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    return Response({"token": token.key, "user": serializer.data})

@api_view(['POST'])
def signup(request):
    # creating a serializer based on the request
    serializer = UserSerializer(data=request.data)
    # if we have our fields (username, password and email)
    if serializer.is_valid():
        serializer.save()
        # create the user, fetch the user and save password as a hash
        user = User.objects.get(username=request.data['username'])
        user.first_name = request.data['first_name']
        user.last_name = request.data['last_name']
        user.set_password(request.data['password'])
        user.save()
        UserProfile.objects.create(user=user)
        # create a token for the user and return their data
        token = Token.objects.create(user=user)
        return Response({"token": token.key, "user": serializer.data})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# imports form authentications within sessions
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])   # checks the request Token and cross reference with DB 
@permission_classes([IsAuthenticated])      # after if the user is authenticated, it sets request as that user
def test_token(request):
    return Response("passed for {}".format(request.user.email))

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    request.auth.delete()  # delete the user token from db
    return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    profile = UserProfile.objects.get(user=request.user)
    serializer = UserProfileSerializer(profile, context={'request': request})
    data = serializer.data
    data['username'] = request.user.username
    data['email'] = request.user.email
    return Response(data)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_to_portfolio(request):
    ticker = request.data.get('ticker')
    name = request.data.get('name', '')  
    if not ticker:
        return Response({"detail": "Ticker is required"}, status=400)

    stock, created = Stock.objects.get_or_create(ticker=ticker, defaults={'name': name})
    profile = UserProfile.objects.get(user=request.user)
    profile.portfolio.add(stock)
    return Response({"detail": f"{ticker} added to portfolio."})


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_to_watchlist(request):
    ticker = request.data.get('ticker')
    name = request.data.get('name', '')
    if not ticker:
        return Response({"detail": "Ticker is required"}, status=400)

    stock, created = Stock.objects.get_or_create(ticker=ticker, defaults={'name': name})
    profile = UserProfile.objects.get(user=request.user)
    profile.watchlist.add(stock)
    return Response({"detail": f"{ticker} added to watchlist."})

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def remove_from_portfolio(request):
    ticker = request.data.get('ticker')
    if not ticker:
        return Response({"detail": "Ticker is required"}, status=400)

    try:
        stock = Stock.objects.get(ticker=ticker)
    except Stock.DoesNotExist:
        return Response({"detail": f"{ticker} not found."}, status=404)

    profile = UserProfile.objects.get(user=request.user)
    profile.portfolio.remove(stock)
    return Response({"detail": f"{ticker} removed from portfolio."})


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def remove_from_watchlist(request):
    ticker = request.data.get('ticker')
    if not ticker:
        return Response({"detail": "Ticker is required"}, status=400)

    try:
        stock = Stock.objects.get(ticker=ticker)
    except Stock.DoesNotExist:
        return Response({"detail": f"{ticker} not found."}, status=404)

    profile = UserProfile.objects.get(user=request.user)
    profile.watchlist.remove(stock)
    return Response({"detail": f"{ticker} removed from watchlist."})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def portfolio_list(request):
    profile = UserProfile.objects.get(user=request.user)
    serializer = StockSerializer(profile.portfolio.all(), many=True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def watchlist_list(request):
    profile = UserProfile.objects.get(user=request.user)
    serializer = StockSerializer(profile.watchlist.all(), many=True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def is_in_watchlist(request, ticker):
    try:
        stock = Stock.objects.get(ticker=ticker)
        profile = UserProfile.objects.get(user=request.user)
        is_present = profile.watchlist.filter(pk=stock.pk).exists()
        return Response({"is_in_watchlist": is_present})
    except Stock.DoesNotExist:
        return Response({"is_in_watchlist": False})

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    profile = UserProfile.objects.get(user=request.user)
    avatar = request.FILES.get('avatar')
    if not avatar:
        return Response({"detail": "No avatar uploaded."}, status=400)
    profile.avatar = avatar
    profile.save()
    return Response({"detail": "Avatar updated.", "avatar_url": request.build_absolute_uri(profile.avatar.url)})



