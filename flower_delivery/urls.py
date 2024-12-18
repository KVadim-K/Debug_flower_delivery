# flower_delivery/urls.py

from django.contrib import admin
from django.urls import path, include
from .views import home
from django.conf import settings
from django.conf.urls.static import static
from users.views import telegram_callback  # Импортируем нашу функцию для Telegram callback
from . import views

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
    path('oauth/', include('social_django.urls', namespace='social')),
    path('oauth/complete/telegram-callback/', telegram_callback, name='telegram_callback'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
