from django.contrib import admin
from .models import NotificationLog

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('payment', 'attempt_number', 'outcome', 'duration_ms', 'created_at')
    list_filter = ('outcome', 'created_at')
    search_fields = ('payment__payment_id',)
    readonly_fields = ('id', 'payment', 'attempt_number', 'outcome', 'duration_ms', 'error_message', 'created_at')
    
    def has_add_permission(self, request):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False
