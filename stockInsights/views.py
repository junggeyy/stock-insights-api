# views moved to user/views.py
from rest_framework.decorators import api_view 
from rest_framework.response import Response    


@api_view(['GET'])
def test(request):
    return Response({"message":"Welcome to Stock Insights!"})