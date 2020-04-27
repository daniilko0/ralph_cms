from django.contrib import admin

from .models import Administrators
from .models import FinancesCategories
from .models import Groups
from .models import Mailings
from .models import Schedule
from .models import Subscriptions
from .models import UsersInfo

admin.site.register(Administrators)
admin.site.register(FinancesCategories)
admin.site.register(Groups)
admin.site.register(Mailings)
admin.site.register(Schedule)
admin.site.register(Subscriptions)
admin.site.register(UsersInfo)
