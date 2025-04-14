from django.contrib import admin
from rbac.models import Role,UserInfo,Permission,PermGroup,Menu
# Register your models here.
admin.site.register(Role)
admin.site.register(UserInfo)
admin.site.register(Permission)
admin.site.register(PermGroup)
admin.site.register(Menu)