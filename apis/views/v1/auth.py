
# ---------- Python's Libraries ---------------------------------------------------------------------------------------
import os
import json

# ---------- Django Tools Rest Framework, Oauth 2 Tools ---------------------------------------------------------------
from django.utils import timezone
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters

from rest_framework import status as http_status
import oauth2_provider.views as oauth2_views
from oauth2_provider.signals import app_authorized
from oauth2_provider.models import get_access_token_model

# ---------- Created Tools --------------------------------------------------------------------------------------------
from apis.models import User


class ApiEndpoint(oauth2_views.TokenView):

    @staticmethod
    def get(request, *args, **kwargs):
        return HttpResponse('Hello, OAuth2!')

    @method_decorator(sensitive_post_parameters('password'))
    def post(self, request, *args, **kwargs):

        if (username := request.POST.get('username').lower()) is None:
            return HttpResponse({'message': "Email field can't blank."}, tatus=http_status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, email=username)
        if user.is_active is False:
            return HttpResponse({'message': 'User is not active. Please contact your corporate admin.'},
                                status=http_status.HTTP_400_BAD_REQUEST, content_type="application/json")

        context = self.get_user_context(user)
        url, headers, body, status = self.create_token_response(request)

        if status == http_status.HTTP_400_BAD_REQUEST:
            return HttpResponse(content=body, status=status, content_type="application/json")

        if status == http_status.HTTP_200_OK:
            access_token = json.loads(body).get('access_token')
            if access_token is not None:
                token = get_access_token_model().objects.get(token=access_token)
                app_authorized.send(sender=self, request=request, token=token)

        context['token'] = json.loads(body)

        response = HttpResponse(content=json.dumps(context), status=status)
        for k, v in headers.items():
            response[k] = v

        user.last_login = timezone.now()
        user.save()

        return response

    @staticmethod
    def get_user_context(user):

        user_data = {'id': user.pk,
                     'first_name': user.first_name,
                     'last_name': user.last_name,
                     'shortcut_name': user.shortcut_name,
                     'username': user.username,
                     'email': user.email,
                     'is_accept_terms': user.is_accept_terms,
                     'is_superuser': user.is_superuser,
                     'permission_corporate': user.permission, }

        return user_data

    def create_token_response(self, request):
        return super(oauth2_views.TokenView, self).create_token_response(request)