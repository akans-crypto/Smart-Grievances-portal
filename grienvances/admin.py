from django.contrib import admin
from grienvances.models import Complaint, Response, Feedback, ContactMessage

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("subject", "user", "status", "priority", "created_at")
    list_filter = ("status", "priority", "created_at")
    search_fields = ("subject", "description", "user__username")
    actions = ["mark_resolved"]

    def mark_resolved(self, request, queryset):
        queryset.update(status="Resolved")
        self.message_user(request, "Selected complaints marked as resolved.")
    mark_resolved.short_description = "Mark selected complaints as resolved"


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'admin', 'created_at')
    search_fields = ('complaint__description', 'admin__username')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'user', 'rating', 'created_at')
    search_fields = ('complaint__description', 'user__username', 'comments')

admin.site.register(ContactMessage)
