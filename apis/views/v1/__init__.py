# ---------- Python's Libraries ---------------------------------------------------------------------------------------
import sys
import uuid

# ---------- Django Tools Rest Framework, Oauth 2 Tools ---------------------------------------------------------------
from django.db.models import Q
from django.conf import settings
from django.core.cache import cache
# from django.shortcuts import get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
# from django.contrib.contenttypes.models import ContentType

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied, NotFound, ParseError

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, OAuth2Authentication

# ---------- Created Tools --------------------------------------------------------------------------------------------
from apis import utils
from apis.models import WorkSpaceUsers


class OAuthPermission:
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope]


class OAuthAPIView(OAuthPermission, APIView):

    def get_workspace(self):

        if not (work_space := self.request.query_params.get("workspace")):
            raise ParseError(detail=f"Please specify Facility ID in query param.")


        if not self.request.user.is_superuser and not WorkSpaceUsers.objects.filter(user=self.request.user,
                                                                                   workspace=work_space).exists():
            raise PermissionDenied(detail="You don't have permission to access this Location.")

        return work_space


class OAuthProjectAPIView(OAuthAPIView):
    @staticmethod
    def tool_check(tool):
        if tool == "Facility":
            return True
        else:
            return False

    def check_permission_tool(self, facility, tool, level, return_false=False):

        if not self.request.user.is_superuser and tool not in ['User_Group', "User_Roles", "Priorities", "Discipline"]:
            try:
                facility_user = FacilityUsers.objects.get(user=self.request.user, facility=facility)
                tool_label = ToolLabels.objects.get(title=tool)
                permission = PermissionToolsLabel.objects.get(tool_label=tool_label,
                                                              permission_template=facility_user.permission_template)

                if permission.permission_level < level:
                    if return_false:
                        return False

                    if self.tool_check(tool):
                        return []

                    raise PermissionDenied(detail=f"User {self.request.user.full_name} Permission denied.")

                return True

            except ObjectDoesNotExist:
                if self.tool_check(tool):
                    return []
                else:
                    raise PermissionDenied(detail=f"User {self.request.user.full_name} Permission denied.")

            # except Exception as ex:
            #     exc_type, exc_obj, exc_tb = sys.exc_info()
            #     print(f"\n\nExcept type {type(ex).__name__}, Arguments: {ex.args!r} in Line {exc_tb.tb_lineno}\n.")
            #
            #     raise ParseError(detail="Something went wrong.")

        return True

    def get_user_in_user_group(self, user_group_id_list, tool, level="none"):
        permission_level_list = ["none", "view_only", "general", "admin"]

        facility = self.get_facility()
        user_group_id_list = user_group_id_list if type(user_group_id_list) == list else [user_group_id_list]
        user_group_list = UserGroup.objects.filter(pk__in=user_group_id_list)

        # ---------- Get ContentType by tool (and make sure that tool is available) -----------------------------------
        try:
            tool_label = ToolLabels.objects.get(title=tool)

        except ObjectDoesNotExist:
            return Response({"message": "Tool not Found."}, status=status.HTTP_400_BAD_REQUEST)

        # ---------- Get Permission Template by Level (level: none, view only, general and admin) ---------------------
        int_level = permission_level_list.index(level)

        perm_tool_label = PermissionToolsLabel.objects.filter(tool_label=tool_label, permission_level__gte=int_level
                                                              ).values("permission_template")

        if not perm_tool_label.exists():
            return Response({"message": f"Permission Level '{level}' not Found."}, status=status.HTTP_400_BAD_REQUEST)

        # ---------- Filter User that have Permission and append User List --------------------------------------------
        group_member = []
        for user_group in user_group_list:
            group_member.extend([member.pk for member in user_group.member.all()])

        return [member.user.pk for member in FacilityUsers.objects.filter(
            Q(facility=facility) &
            Q(permission_template__pk__in=perm_tool_label) &
            Q(user__pk__in=list(set(group_member)))
        ).order_by("user__pk")]
