from django.contrib.admin import ModelAdmin, register, TabularInline
from django.contrib.auth import get_user_model

User = get_user_model()


class ContractZoneInline(TabularInline):
    model = User.contract_zones.through
    extra = 0


@register(User)
class UserAdmin(ModelAdmin):
    fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "date_joined",
        "last_login",
        "is_active",
        "is_superuser",
        "is_official",
        "department_name",
        "ad_groups",
    )
    inlines = (ContractZoneInline,)

    def get_readonly_fields(self, request, obj=None):
        fields = ("date_joined", "last_login")
        return fields + ("username",) if obj else fields
