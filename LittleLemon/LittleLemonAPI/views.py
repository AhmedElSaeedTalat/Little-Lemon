from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import MenuItem, Cart
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator, EmptyPage


class MenuItemsView(APIView):
    """ class menu items to view all items """
    def get(self, request, menuItem=None):
        """ retrieve one item """
        if menuItem:
            item = get_object_or_404(MenuItem, pk=menuItem)
            item = MenuItemSerializer(item)
            return Response(item.data)
        """ pagination params """
        perpage = request.query_params.get('perpage', default=2)
        page = request.query_params.get('page', default=1)
        """ retrieve all items """
        items = MenuItem.objects.select_related('category').all()
        pagination = Paginator(items, per_page=perpage)
        try:
            items = pagination.page(number=page)
        except EmptyPage:
            items = []
        items = MenuItemSerializer(items, many=True)
        return Response(items.data)
 
    @permission_classes([IsAuthenticated])
    def post(self, request):
        """ post menuItem"""
        if request.user.groups.filter(name='Maneger').exists():
            data = MenuItemSerializer(data=request.data)
            data.is_valid(raise_exception=True)
            data.save()
            return Response(data.data, 201)
        else:
            return Response('Unauthorized', 403)
    
    @permission_classes([IsAuthenticated])
    def patch(self, request, menuItem):
        """ update menu item"""
        if request.user.groups.filter(name='Maneger').exists():
            item = get_object_or_404(MenuItem, pk = menuItem)
            patch_data = MenuItemSerializer(instance=item, data=request.data, partial=True)
            patch_data.is_valid(raise_exception=True)
            patch_data.save()
            return Response(patch_data.data)
        else:
            return Response('Unuathorized', 403)

    @permission_classes([IsAuthenticated])
    def put(self, request, menuItem):
        """ update menu item through put method"""
        if request.user.groups.filter(name='Maneger').exists():
            item = get_object_or_404(MenuItem, pk=menuItem)
            put_data = MenuItemSerializer(instance=item, data=request.data)
            put_data.is_valid(raise_exception=True)
            put_data.save()
            return Response(put_data.data)
        else:
            return Response('Unauthorized', 403)
    
    @permission_classes([IsAuthenticated])
    def delete(self, request, menuItem):
        """ delete item from the menu """
        if request.user.groups.filter(name='Maneger').exists():
            item = get_object_or_404(MenuItem, pk=menuItem)
            item.delete()
            return Response({})
        else:
            return Response('Unauthorized', 403)

@permission_classes([IsAuthenticated])
class CartView(APIView):
    """ cart view """
    def get(self, request):
        user_id = request.user.id
        items = Cart.objects.filter(user_id=user_id)
        context = {'request':request}
        items = CartSerializer(items, many=True, context=context)
        return Response(items.data)

    def post(self, request):
        """ deal with payload """
        context = {'request':request}
        info = CartSerializer(data=request.data, context=context)
        info.is_valid(raise_exception=True)
        info.save()
        return Response('item is added')
    
    def delete(self, request):
        """ delete all menu items """
        user_id = request.user.id
        Cart.objects.filter(user_id=user_id).delete()
        return Response('All items got deleted')
