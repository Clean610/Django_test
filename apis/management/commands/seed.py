
# ---------- Python's Libraries ---------------------------------------------------------------------------------------

# ---------- Django Tools Rest Framework, Oauth 2 Tools ---------------------------------------------------------------
from django.core.management import BaseCommand
from django.contrib.auth.models import Group

# ---------- Created Tools --------------------------------------------------------------------------------------------
from apis.utils import PERMISSION_LEVEL_ADMIN
from apis.models import User
from apis.management.commands.seeders import seed_user
from apis import utils


class Command(BaseCommand):
    def handle(self, *args, **options):
        # self.user_seeder()

        self.group_seeder()
        # self.priority_seeder()
        # self.permission_seeder()

    @staticmethod
    def user_seeder():
        for user in seed_user.dataset:
            if not User.objects.filter(email=user["email"].lower()).exists():
                User.objects.create_user(email=user["email"].lower(),
                                         username=user["username"],
                                         password=user["password"],
                                         first_name=user["first_name"],
                                         position=user["position"],
                                         last_name=user["last_name"],
                                         )

    @staticmethod
    def group_seeder():
        for permission_group in ["admin", "user", "manager"]:
            Group.objects.get_or_create(name=f"{permission_group}")

    #
    # @staticmethod
    # def priority_seeder():
    #     for priority in ["Low Priority", "Medium Priority", "High Priority"]:
    #         Priorities.objects.get_or_create(title=f"{priority}", facility=None)




