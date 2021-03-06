from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


# admin.site.register(User, UserAdmin)
from django.contrib.auth.forms import UserChangeForm


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm

    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('profile_picture', 'new_email')}),
    )


admin.site.register(User, MyUserAdmin)

