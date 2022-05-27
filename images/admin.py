from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Plan, Image, PlanHeight, TemporaryLink


class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = (
        (
            'Plan',
            {
                'fields': (
                    'account_tier',
                )
            }
        ),
        *UserAdmin.fieldsets
    )


class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'original_link', 'generate_links')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(Image)
admin.site.register(PlanHeight)
