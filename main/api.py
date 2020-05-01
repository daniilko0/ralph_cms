from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import Permission
from django.contrib.auth.models import User

from sesame import utils


class AuthLinkView(APIView):
    def get(self, request, group):
        try:
            perm = Permission.objects.get(codename__contains=str(group))
        except Permission.DoesNotExist:
            return Response(
                {
                    "result": {
                        "code": 400,
                        "description": "[400] Permission doesn't exist",
                    }
                }
            )
        try:
            user = User.objects.get(user_permissions=perm, is_superuser=False)
        except User.DoesNotExist:
            return Response(
                {"result": {"code": 400, "description": "[400] User doesn't exist",}}
            )
        link_data = utils.get_parameters(user)
        return Response(
            {"result": {"code": 200, "description": "[200] OK", "link": link_data}}
        )
