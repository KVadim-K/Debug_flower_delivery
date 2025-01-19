# flower_delivery/urls.py

from django.contrib import admin
from django.urls import path, include
from .views import home
from django.conf import settings
from django.conf.urls.static import static
from users.views import telegram_callback  # Импортируем нашу функцию для Telegram callback
from . import views
from flower_delivery.views import clear_cache
from django.http import JsonResponse
from django.views.generic.base import RedirectView
# from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
# def debug_view(request):
#    return JsonResponse({
#        "method": request.method,
#        "GET": dict(request.GET),
#        "POST": dict(request.POST),
#    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('accounts/', include('allauth.urls')),  # Маршруты django-allauth
    path('', views.home, name='home'),
    path('products/', include('products.urls', namespace='products')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('reviews/', include('reviews.urls', namespace='reviews')),
    path('reports/', include('reports.urls', namespace='reports')),
    path('api/link_telegram_id/', views.link_telegram_id, name='link_telegram_id'),
#    path('oauth/complete/telegram/', debug_view),  # Временная отладка
    path('oauth/', include('social_django.urls', namespace='social')),
    path('clear-cache/', clear_cache, name='clear_cache'),
    path('oauth/complete/telegram-callback/', telegram_callback, name='telegram_callback'),
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'img/favicon.ico', permanent=True)),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
