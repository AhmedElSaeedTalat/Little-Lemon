from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import MenuItem
from .serializers import MenuItemSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator, EmptyPage


@permission_classes([IsAuthenticated])
class UsersView(APIView):
    """ class to deal with users methods """
    def get(self, request, userId=None):
        if request.user.groups.filter(name='Maneger').exists():
            users = User.objects.filter(groups=1)
            """ params """
            perpage = request.query_params.get('perpage', default=2)
            page = request.query_params.get('page', default=1)
            pagination = Paginator(users, per_page=perpage)
            try:
                users = pagination.page(number=page)
            except EmptyPage:
                users = []
            users = UserSerializer(users, many=True)
            return Response(users.data)
        else:
            return Response('Unauthorized', 403)

    def post(self, request):
        """ assign user in the payload to Maneger """
        if request.user.groups.filter(name='Maneger').exists():
            passed_user = request.data.get('username')
            if passed_user:
                user = get_object_or_404(User, username=passed_user)
                manegerGroup = Group.objects.get(name='Maneger')
                manegerGroup.user_set.add(user)
                return Response({"message": "added user to Mangers"}, 201)
            else:
                return Response({"message": "please pass a valid username"}, 400)
        else:
                return Response('Unauthorized', 403)
    
    def delete(self, request, userId):
        """delete user from maneger groups"""
        if request.user.groups.filter(name='Maneger').exists():
            user = get_object_or_404(User, pk=userId)
            group = Group.objects.get(name='Maneger')
            group.user_set.remove(user)
            return Response({"message":"user got removed"})
        else:
            return Response('Unauthorized', 403)



@permission_classes([IsAuthenticated])
class DeliveryCrewView(APIView):
    def get(self, request):
        """ display user relate to delivery crew"""
        if request.user.groups.filter(name='Maneger').exists():
            users = User.objects.filter(groups=2)
            users = UserSerializer(users, many=True)
            return Response(users.data)
        else:
            return Response('Unauthorized', 403)
    
    def post(self, request):
        """ assign passed user to delivery crew"""
        if request.user.groups.filter(name='Maneger'):
            try:
                username = request.data.get('username')
                user = get_object_or_404(User, username=username)
                group = Group.objects.get(name='Delivery crew')
                group.user_set.add(user)
                return Response('user added to the Delivery crew')
            except UnboundLocalError:
                return Response('please pass username', 400)
        else:
            return Response('Unauthorized', 403)

    def delete(self, request, userId):
        """delete user from group """
        if request.user.groups.filter(name='Maneger'):
            user = get_object_or_404(User, pk=userId)
            group = Group.objects.get(name='Delivery crew')
            group.user_set.remove(user)
            return Response({"user removed from Delivery crew"})
        else:
            return Response('Unauthorized', 403)