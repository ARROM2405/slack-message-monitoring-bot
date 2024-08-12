from django.contrib import admin

from slack_integration.models import (
    DataSecurityPattern,
    DataLossMessage,
    DataLossMessageQuerySet,
)


@admin.register(DataSecurityPattern)
class DataSecurityPatternAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "pattern")
    list_filter = ("name",)
    search_fields = ("name",)


class DataSecurityPatternInline(admin.TabularInline):
    model = DataLossMessage.failed_security_patterns.through
    # readonly_fields = ("id", "name", "pattern")
    extra = 0


class HasFileFilter(admin.SimpleListFilter):
    title = "has file"
    parameter_name = "has_file"

    def lookups(self, request, model_admin):
        return [
            ("yes", "Yes"),
            ("no", "No"),
        ]

    def queryset(self, request, queryset: DataLossMessageQuerySet):
        if self.value() == "yes":
            return queryset.annotate_has_file().filter(has_file=True)
        if self.value() == "no":
            return queryset.annotate_has_file().filter(has_file=False)
        return queryset


@admin.register(DataLossMessage)
class DataLossMessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "text",
        "has_file",
        "ts",
        "channel",
    )
    search_fields = (
        "ts",
        "channel",
    )

    def has_file(self, obj):
        return obj.has_file

    list_filter = [HasFileFilter]

    inlines = (DataSecurityPatternInline,)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).annotate_has_file()
