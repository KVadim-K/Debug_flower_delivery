# orders/views.py

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from cart.models import Cart, CartItem
from .models import Order, OrderItem
from products.models import Product
from django.utils import timezone
from rest_framework import generics, permissions
from .serializers import OrderSerializer, OrderStatusSerializer, OrderAnalyticsSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
from .forms import OrderDeliveryForm
# Избегаем дублирования сигнала через send_notification_to_admins.delay(order.id)
# from telegramadmin_bot.tasks import send_notification_to_admins

@login_required
def create_order(request, product_id=None):
    """
    Создание заказа через веб-интерфейс с указанием данных для доставки.
    """
    # Получаем корзину текущего пользователя или создаём новую
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Если передан product_id, добавляем товар в корзину
    if product_id:
        product = get_object_or_404(Product, id=product_id)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
        if item_created:
            cart_item.quantity = 1  # Устанавливаем количество, если товар новый в корзине
        else:
            cart_item.quantity += 1  # Увеличиваем количество, если товар уже добавлен
        cart_item.save()

    # Проверяем, не пуста ли корзина
    if not cart.items.exists():
        return redirect('cart:cart_detail')

    # Обработка создания заказа при POST-запросе
    if request.method == 'POST':
        form = OrderDeliveryForm(request.POST)
        if form.is_valid():
            # Получаем данные доставки из формы
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            postal_code = form.cleaned_data['postal_code']
            phone_number = form.cleaned_data['phone_number']

            # Создаём заказ
            order = Order.objects.create(
                user=request.user,
                status='pending',
                created_at=timezone.now(),
                address=address,
                city=city,
                postal_code=postal_code,
                phone_number=phone_number
            )

            # Переносим товары из корзины в заказ
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )

            # Вычисляем общую сумму заказа
            total_price = sum(item.product.price * item.quantity for item in order.order_items.all())
            order.total_price = total_price
            order.save()

            # Очищаем корзину после создания заказа
            cart.items.all().delete()

            # Уведомляем администраторов о новом заказе через Celery
            # send_notification_to_admins.delay(order.id)

            return redirect('orders:order_history')
        else:
            # Если форма не валидна, отобразить ошибки
            context = {
                'cart': cart,
                'form': form
            }
            return render(request, 'orders/create_order.html', context)
    else:
        form = OrderDeliveryForm()

    # Рендерим шаблон создания заказа с текущей корзиной и формой
    return render(request, 'orders/create_order.html', {'cart': cart, 'form': form})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('order_items').order_by('-created_at')

    # Вычисляем итоговую сумму для каждого заказа
    for order in orders:
        total_price = 0
        for item in order.order_items.all():
            total_price += item.quantity * item.product.price
        order.total_price = total_price

    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def reorder(request, order_id):
    original_order = get_object_or_404(Order, id=order_id, user=request.user)

    if not original_order.order_items.exists():
        print("Исходный заказ не содержит товаров.")
        return redirect('orders:order_history')

    # Получаем или создаём корзину пользователя
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Переносим товары из заказа в корзину
    for item in original_order.order_items.all():
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=item.product)
        if created:
            cart_item.quantity = item.quantity
        else:
            cart_item.quantity += item.quantity
        cart_item.save()

    return redirect('cart:cart_detail')


@login_required
def update_cart(request):
    cart = Cart.objects.get(user=request.user)
    for item in cart.items.all():
        quantity = request.POST.get(f'quantity_{item.id}')
        if quantity:
            try:
                quantity = int(quantity)
                if quantity > 0:
                    item.quantity = quantity
                    item.save()
                else:
                    item.delete()
            except ValueError:
                pass  # Игнорируем некорректные значения
    return redirect('cart:cart_detail')


# API-представления

class CreateOrderAPIView(generics.CreateAPIView):
    """
    API-представление для создания нового заказа.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderStatusAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        serializer = OrderStatusSerializer(order)
        return Response(serializer.data)


class OrderAnalyticsAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        total_orders = Order.objects.count()
        total_sales = Order.objects.aggregate(Sum('order_items__product__price'))['order_items__product__price__sum'] or 0
        total_profit = total_sales * 0.2
        total_expenses = total_sales * 0.8
        data = {
            'total_orders': total_orders,
            'total_sales': total_sales,
            'total_profit': total_profit,
            'total_expenses': total_expenses,
        }
        serializer = OrderAnalyticsSerializer(data)
        return Response(serializer.data)


class UserOrdersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
