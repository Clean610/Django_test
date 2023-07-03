# ---------- Python's Libraries ---------------------------------------------------------------------------------------
from datetime import timedelta
import datetime

# ---------- Django Tools Rest Framework, Oauth 2 Tools ---------------------------------------------------------------
import django_filters

from django.db.models import Q
from django.utils import timezone
from django.db.models.functions import Concat
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import CharField, F, DurationField, ExpressionWrapper, Value as V

# ---------- Created Tools --------------------------------------------------------------------------------------------
from apis import utils
from apis.models import User


class UserFilter(django_filters.FilterSet):
    # --------------Date---------------- #
    created_at = django_filters.DateFromToRangeFilter(field_name='created_at')
    last_login = django_filters.DateFromToRangeFilter(field_name='last_login')

    # --------------User---------------- #
    created_by = django_filters.ModelChoiceFilter(field_name='user', queryset=User.objects.all())

    # --------------Text---------------- #
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')
    first_name = django_filters.CharFilter(field_name='first_name', lookup_expr='icontains')
    last_name = django_filters.CharFilter(field_name='last_name', lookup_expr='icontains')
    position = django_filters.CharFilter(field_name='position', lookup_expr='icontains')

    # --------------Other---------------- #
    is_verified = django_filters.BooleanFilter(field_name='is_verified')
    search = django_filters.CharFilter(method='search_user')

    @staticmethod
    def search_user(queryset, name, value):
        return queryset.filter(Q(email__icontains=value) | Q(first_name__icontains=value) |
                               Q(last_name__icontains=value) | Q(position__icontains=value) |
                               Q(username__icontains=value) | Q(phone__icontains=value))

    class Meta:
        model = User
        fields = ['created_at', 'last_login', 'created_by', 'email', 'first_name', 'last_name', 'position',
                  'is_verified', 'search', ]