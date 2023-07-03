# ---------- Python's Libraries ---------------------------------------------------------------------------------------
import re


# ---------- Django Tools Rest Framework, Oauth 2 Tools ---------------------------------------------------------------
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q, JSONField
from rest_framework.exceptions import ValidationError

from safedelete.models import SafeDeleteModel, SOFT_DELETE


# ---------- Created Tools --------------------------------------------------------------------------------------------
from apis import utils, managers


# ========= Base Model ================================================================================================
class BaseModel(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    original_objects = models.Manager()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(BaseModel, AbstractUser):
    email = models.EmailField(max_length=255, verbose_name='email address', unique=True, blank=False, null=False)
    objects = managers.UserSafeDeleteManager()
    created_by = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                   related_name='user_created_by')
    position = models.CharField(null=True, blank=True, max_length=255)
    permission = models.IntegerField(default=0, choices=utils.CHOICE_PERMISSION_LEVEL)
    is_accept_terms = models.BooleanField(default=False)
    accept_terms_date = models.DateField(blank=True, null=True, default=None)
    is_verified = models.BooleanField(default=False)
    verify_key = models.CharField(max_length=255, null=True, blank=True)
    verify_key_expires = models.DateTimeField(blank=True, null=True, default=None)
    phone = models.CharField(null=True, blank=True, max_length=50)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.get_full_name()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def shortcut_name(self):
        return re.sub(r"[^A-Z]", r"", self.get_full_name().title())

    @property
    def details_context(self):
        return {
            'id': self.pk,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'position': self.position,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'shortcut_name': self.shortcut_name,
            'is_accept_terms': self.is_accept_terms,
            'permission_corporate': self.permission
        }

    @property
    def list_context(self):
        return {
            'id': self.pk,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'shortcut_name': self.shortcut_name,
            'email': self.email,
            'position': self.position,
            'phone': self.phone
        }

    @property
    def choices_context(self):
        return {"value": self.pk, "label": f"{self.first_name} {self.last_name}"}

# ========= Workspace Level ============================================================================================
class WorkSpace(BaseModel):
    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE,
                                   related_name="workspace_created_by")
    updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE,
                                   related_name="workspace_updated_by")

    @property
    def details_context(self):
        return {
            'id': self.pk,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    class Meta:
        constraints = [models.UniqueConstraint(fields=["title"],
                                               condition=Q(deleted__isnull=True), name="unique_workspace")]

class DocumentFlow(BaseModel):
    title = models.CharField(max_length=100, null=False, blank=False, unique=True)
    is_active = models.BooleanField()
    process = models.IntegerField()
    uuid = models.UUIDField()
    workspace = models.ForeignKey(WorkSpace, blank=False, null=False, on_delete=models.CASCADE)

# ========= Custom Form & Instruction =================================================================================

class CustomForms(BaseModel):
    title = models.CharField(max_length=255, blank=False, null=False)
    source = JSONField()
    workspace = models.ForeignKey(WorkSpace, blank=False, null=False, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)

    @property
    def details_context(self):
        return {
            'id': self.pk,
            'title': self.title,
            'source': self.source,
            'created_by': self.created_by.list_context,
        }

    @property
    def choices_context(self):
        return {"value": self.pk, "label": self.title}

    class Meta:
        constraints = [models.UniqueConstraint(fields=["title", "workspace"],
                                               condition=Q(deleted__isnull=True), name="unique_custom_form")]

class InstructionFlow(BaseModel):
    document_flow = models.ForeignKey(DocumentFlow, blank=False, null=False , on_delete=models.CASCADE)
    title = models.CharField(blank=False, null=False, max_length=225)
    section = models.IntegerField(blank=False, null=False)
    section_title = models.CharField(blank=False, null=False, max_length=225)
    sub_section = models.IntegerField(blank=False, null=False)
    response = models.CharField(blank=True, null=True, max_length=225)
    responder = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)
    is_open = models.BooleanField(blank=False, null=False , default=True)
    type = models.IntegerField(choices=utils.CHOICE_FORM_TYPE, null=False, blank=False)
    value_option = models.JSONField(blank=True, null=True , default=dict)
    file = models.FileField(upload_to='image/', blank=True, null=True)

    @property
    def details_context(self):
        return {
            'id': self.pk,
            'title': self.title,
            'section': self.section,
            'section_title': self.section_title,
            'subsection': self.sub_section,
            'type': self.type,
            'value_option': self.value_option if self.value_option else [],
            'response': self.response,
            'responder': self.responder.list_context if self.responder else None,
            'is_open': self.is_open,
        }

    @property
    def list_context(self):
        return {
            'id': self.pk,
            'title': self.title,
            'section': self.section,
            'section_title': self.section_title,
            'subsection': self.sub_section,
            'type': self.type,
        }

    def clean(self, *args, **kwargs):
        if (utils.FORMS_INSTRUCTIONS_TYPE_OPTION_LIST <= self.type <= utils.FORMS_INSTRUCTIONS_TYPE_PDF_FIELD) \
                and self.value_option is None:
            raise ValidationError("Field 'value_option' can't be null in this form type.")

        return super().clean(*args, **kwargs)


# ========= Permission Template & User Permission =====================================================================

class PermissionTemplate(BaseModel):
    title = models.CharField(max_length=100, null=False, blank=False)
    workspace = models.ForeignKey(WorkSpace, null=False ,blank=False, on_delete=models.CASCADE)


    @property
    def details_context(self):
        return {
            "id": self.pk,
            "title": self.title,
            "permission_tool": [permission_tool.details_context for permission_tool in
                                Permission.objects.filter(permission_template=self)]
        }

    @property
    def list_context(self):
        return {"id": self.pk, "title": self.title, }

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title'], condition=Q(deleted__isnull=True),
                                    name='unique_permission_template')
        ]


class Permission(BaseModel):
    permission_template = models.ForeignKey(PermissionTemplate, on_delete=models.CASCADE, null=False, blank=False)
    permission_level = models.IntegerField(choices=utils.CHOICE_PERMISSION_LEVEL, default=utils.PERMISSION_LEVEL_NONE,
                                           null=False, blank=False)


class WorkSpaceUsers(BaseModel):
    workspace = models.ForeignKey(WorkSpace, null=False, blank=False, on_delete=models.CASCADE)
    permission_template = models.ForeignKey(PermissionTemplate, null=True, blank=False, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE, related_name="workspace_user")
    created_by = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE, related_name="creator")
    updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="moderator")

    @property
    def details_context(self):
        return {
            'id': self.pk,
            'workspace': self.workspace.details_context,
            'user': self.user.list_context,
            'permission_template': self.permission_template.details_context if self.permission_template else None,
            'created_at': self.created_at,
            'created_by': self.created_by.list_context,
            'updated_by': self.updated_by.list_context if self.updated_by else None,
        }

    @property
    def choices_context(self):
        return {"value": self.user.pk, "label": f"{self.user.full_name}"}

    class Meta:
        constraints = [models.UniqueConstraint(fields=['workspace', 'user'], condition=Q(deleted__isnull=True),
                                               name='unique_user_workspace')]

# ========= Logs ======================================================================================================``````````````````````````````````

class Logs(BaseModel):
    object_id = models.IntegerField(db_index=True)
    action = models.CharField(max_length=255, null=False, blank=False)
    action_by = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)

    @property
    def details_context(self):
        return {
            'id': self.pk,
            'action': self.action,
            'action_by': self.action_by.full_name,
        }
