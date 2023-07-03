# ---------- Python's Libraries ---------------------------------------------------------------------------------------
import os
import time
from datetime import datetime

from django.db.models import Q
# ---------- Django Tools Rest Framework, Oauth 2 Tools ---------------------------------------------------------------

from rest_framework import serializers

from django.db import IntegrityError
from django.contrib.auth.models import Group
from apis import utils

# ---------- Created Tools --------------------------------------------------------------------------------------------
from apis.models import User

class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField()
    password_confirmation = serializers.CharField()

    class Meta:
        model = User
        fields = ['password', 'password_confirmation']
        extra_kwargs = {
            'password': {'write_only': True},
            'password_confirmation': {'write_only': True}
        }

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirmation'):
            raise serializers.ValidationError({'password': 'Password must be confirmed correctly.'})
        return super().validate(attrs)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = super().create(validated_data)
        validated_data['email'] = validated_data['email'].lower()
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        validated_data.pop('username', None)
        return super().update(instance, validated_data)
