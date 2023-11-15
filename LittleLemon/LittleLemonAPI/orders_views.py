from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import MenuItem, Cart, Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User, Group
from datetime import date
from django.core.paginator import Paginator, EmptyPage


@permission_classes([IsAuthenticated])
class OrderView(APIView):
    def get(self, request, orderId=None):
        """ display order for each customer """
        user_id = request.user.id
        """ if user authorized is a Maneger """
        if request.user.groups.filter(name='Maneger').exists():
            all_orders = OrderItem.objects.select_related('order').select_related('menuitem').all()
            perpage = request.query_params.get('perpage', default=2)
            page = request.query_params.get('page', default=1)
            pagination = Paginator(all_orders, per_page=perpage)
            try:
                all_orders = pagination.page(number=page)
            except EmptyPage:
                all_orders = []
            all_orders = OrderItemSerializer(all_orders, many=True)
            return Response(all_orders.data)
        """ if user authorized is a delivery crew """
        if request.user.groups.filter(name='Delivery crew').exists():
            related_order = Order.objects.filter(delivery_crew=user_id)
            related_order = OrderSerializer(related_order, many=True)
            return Response(related_order.data)
        """ 
        if orderId is passed return orderItems related to order 
        only if order related to user authenticated
        """
        if orderId:
            orders = Order.objects.get(id=orderId)
            if orders.user.id == user_id:
                ordersItems = OrderItem.objects.filter(order=orderId)
                orders = OrderItemSerializer(ordersItems, many=True)
                return Response(orders.data)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        """ return all order related to authenticated user """
        orders = Order.objects.filter(user_id=user_id)
        """ params """
        perpage = request.query_params.get('perpage', default=2)
        page = request.query_params.get('page', default=1)
        pagination = Paginator(orders, per_page=perpage)
        try:
            orders = pagination.page(number=page)
        except EmptyPage:
            orders = []
        context = {'request': request}
        orders = OrderSerializer(orders, many=True, context=context)
        return Response(orders.data)

    def post(self, request):
        """ post orders """
        user_id = request.user.id
        user = get_object_or_404(User, id=user_id)
        delivery_crew = None
        """ if passed delivery crew as payeload assign it"""
        if request.data.get('delivery_crew'):
            delivery_crew = request.data.get('delivery_crew')
            delivery_crew = get_object_or_404(User, id=delivery_crew)
        ordersItems = Cart.objects.filter(user_id=user_id)
        total = 0
        for item in ordersItems:
            total += item.price
        create_order=Order.objects.create(user=user, delivery_crew=delivery_crew, total=total, 
                                          date=date.today())
        create_order.save()
        for item in ordersItems:
            menuItem = get_object_or_404(MenuItem, id=item.menuitem.id)
            orderItem = OrderItem.objects.create(order=create_order, menuitem=menuItem, 
                                             quantity=item.quantity, unit_price=item.unit_price,
                                             price=item.price)
            orderItem.save()
        Cart.objects.filter(user_id=user_id).delete()
        serialized_order = OrderSerializer(create_order)
        return Response(serialized_order.data)

    def patch(self, request, orderId):
        """ uptate order """
        if request.user.groups.filter(name='Maneger').exists():
            order = Order.objects.get(id=orderId)
            order = OrderSerializer(instance=order, data=request.data, partial=True)
            order.is_valid(raise_exception=True)
            order.save()
            return Response(order.data)
        elif request.user.groups.filter(name='Delivery crew').exists():
            allowed_field = 'status'
            data = request.data
            new_dict = {}
            if 'status' in data:
                new_dict['status'] = data['status']
            order = Order.objects.get(id=orderId)
            update_status = OrderSerializer(instance=order, data=new_dict, partial=True)
            update_status.is_valid(raise_exception=True)
            update_status.save()
            return Response(update_status.data)
        else:
            return Response('Unuathorized', 403)
    
    def delete(self, request, orderId):
        """ deletes an order """
        if request.user.groups.filter(name='Maneger').exists():
            Order.objects.get(id=orderId).delete()
            return Response({'status': 'order is deleted'})
        else:
            return Response('Unuathorized', 403)


