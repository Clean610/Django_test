# ---------- Python's Libraries ---------------------------------------------------------------------------------------
import random
import hashlib
from datetime import timedelta

# ---------- Django Tools Rest Framework, Oauth 2 Tools ---------------------------------------------------------------
from rest_framework import status
from rest_framework.response import Response

from django.utils import timezone
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError
from safedelete.models import SOFT_DELETE_CASCADE

# ---------- Created Tools --------------------------------------------------------------------------------------------
from apps.password_validate import CustomPasswordValidator
# from apis.filter import UserFilter
from apis.utils import get_paginator
from apis.views.v1 import OAuthAPIView
from apis.models import User, WorkSpaceUsers
from apis.serializers import UserSerializer
from apis.filter import UserFilter





class UserListAPIView(OAuthAPIView):

    def get(self, request, *args, **kwargs):
        user_list = [user.details_context for user in UserFilter(request=self.request.GET, queryset=User.objects.filter(
            is_superuser=False, customer__isnull=True).exclude(pk=self.request.user.pk)).qs]

        return Response(user_list, status=status.HTTP_200_OK)


class UserAPIView(OAuthAPIView):
    sort_list = ['last_login', 'first_name', 'last_name', 'email', 'position', 'company', '-last_login', '-first_name',
                 '-last_name', '-email', '-position', '-company']

    def get(self, request, *args, **kwargs):

        users = User.objects.all().order_by("-pk")

        if self.request.query_params.get("work_space", None):
            workspace = self.get_workspace()

            users = users.exclude(id__in=WorkSpaceUsers.objects.filter(workspace=workspace).values_list("user_id",
                                                                                                     flat=True))

        users = UserFilter(request.GET, queryset=users).qs

        if (sort := request.GET.get("sort", None)) in self.sort_list:
            users = users.order_by(sort)

        users, user_count, page = get_paginator(request, users)

        user_list = [user for user in users]

        context = {"count": user_count, "page": page, "result": user_list}

        return Response(context, status=status.HTTP_200_OK)

    @staticmethod
    def generate_activation_key(username):
        chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
        secret_key = get_random_string(20, chars)

        return hashlib.sha256((secret_key + username).encode('utf-8')).hexdigest()

    def post(self, request, *args, **kwargs):

        next_day = timezone.now() + timedelta(days=1)
        user_serializer = UserSerializer(data=request.data)

        request.data["username"] = request.data["email"]
        request.data["password"] = ''.join([f"{random.randrange(10)}" for i in range(10)])

        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        user_req = request.user
        user.user = user_req
        user.verify_key = self.generate_activation_key(user.username)
        user.verify_key_expires = next_day

        user.is_active = False
        user.save()

        return Response(self.get_user_context(user), status=status.HTTP_201_CREATED)

    @staticmethod
    def patch(request, *args, **kwargs):
        return Response(status=status.HTTP_201_CREATED)

    @staticmethod
    def get_user_context(user):

        context = {
            'id': user.pk,
            'position': user.position,
            'email': user.email,
            'last_name': user.last_name,
            'first_name': user.first_name,
            'full_name': user.full_name,
            'last_login': user.last_login,
            'is_active': user.is_active,
            'is_verified': user.is_verified,
            'created_at': user.created_at,
            'updated_at': user.updated_at,
            'created_by': user.created_by.details_context if user.created_by else None,
        }
        return context


class UserDetailAPIView(OAuthAPIView):

    @staticmethod
    def get(request, pk):
        user = get_object_or_404(User, pk=pk)

        return Response(user.list_context, status=status.HTTP_200_OK)

    @staticmethod
    def put(request, *args, **kwargs):
        # has_project_permission((request, 'change_user')
        user = get_object_or_404(User, pk=kwargs['pk'])
        user_serializer = UserSerializer(user, data=request.data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        cache.set('user-{username}'.format(username=user.username), user)

        return Response(user.list_context, status=status.HTTP_200_OK)

    @staticmethod
    def delete(request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get('pk', None))

        facilities_users = WorkSpaceUsers.objects.filter(user=user)
        facilities_users.delete(SOFT_DELETE_CASCADE)

        user.is_active = False
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

class ChangePasswordView(OAuthAPIView):

    @staticmethod
    def patch(request, *args, **kwargs):
        password_validate = CustomPasswordValidator(min_length=8)
        user = request.user
        password = request.data.get("password", None)
        new_password = request.data.get("new_password", None)
        if user.check_password(password):
            if new_password:
                try:
                    password_validate.validate(new_password)
                    user.set_password(new_password)
                    user.save()
                    return Response({'message': "Changed Password Success"}, status=status.HTTP_200_OK)

                except ValidationError as e:
                    return Response({'message': e.message}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'message': "New Password invalid"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': "Old Password invalid"}, status=status.HTTP_403_FORBIDDEN)