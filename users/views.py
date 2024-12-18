# users/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view

User = get_user_model()

@method_decorator(csrf_exempt, name='dispatch')
class LinkTelegramIDAPIView(APIView):
    """
    API View для связывания Telegram ID с учетной записью пользователя.
    """
    def post(self, request):
        data = request.data
        username = data.get('username')
        telegram_id = data.get('telegram_id')

        if not username or not telegram_id:
            return Response({"error": "Необходимо указать username и telegram_id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
            user.telegram_id = telegram_id
            user.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({"message": "Success", "token": token.key}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(csrf_exempt, name='dispatch')
class GetTokenByTelegramIDAPIView(APIView):
    """
    API View для получения API-токена пользователя по его Telegram ID.
    """
    def get(self, request):
        telegram_id = request.query_params.get('telegram_id')
        if not telegram_id:
            return Response({"error": "Необходимо указать telegram_id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(telegram_id=telegram_id)
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": f"Пользователь с telegram_id {telegram_id} не найден."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@csrf_exempt
def telegram_callback(request):
    """
    Обрабатывает POST-запрос от Telegram виджета.
    Предполагается, что пользовательский объект будет в поле 'user' в теле запроса,
    содержащий как минимум 'id' (Telegram user ID), и, возможно, 'username'.
    """
    user_data = request.data
    tg_id = user_data.get('id')  # Telegram user ID
    tg_username = user_data.get('username')

    if not tg_id:
        return Response({"error": "Telegram user id not provided"}, status=status.HTTP_400_BAD_REQUEST)

    # Создаём или получаем пользователя, связанного с данным Telegram ID
    user, created = User.objects.get_or_create(
        username=f'tg_{tg_id}',
        defaults={'telegram_id': tg_id}
    )

    # Получаем или создаём токен для пользователя
    token, _ = Token.objects.get_or_create(user=user)

    return Response({"message": "Telegram auth successful", "token": token.key}, status=status.HTTP_200_OK)
