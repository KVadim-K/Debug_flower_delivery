# flower_delivery/views.py

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()

def home(request):
    return render(request, 'home.html')

@api_view(['POST'])
def link_telegram_id(request):
    username = request.data.get("username")
    telegram_id = request.data.get("telegram_id")

    if not username or not telegram_id:
        return Response({"error": "username and telegram_id are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=username)
        user.telegram_id = telegram_id
        user.save()
        return Response({"message": "Telegram ID linked successfully."}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
@api_view(['POST'])
def clear_cache(request):
    """
    Очищает весь кэш сервера.
    """
    cache.clear()
    return Response({"message": "Кэш успешно очищен."}, status=status.HTTP_200_OK)

