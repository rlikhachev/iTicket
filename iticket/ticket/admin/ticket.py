from django.contrib import admin
from ..models import Ticket, TicketHistory



@admin.register(TicketHistory)
class TicketHistoryAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class TicketHistoryInlineAdmin(admin.TabularInline):
    model = TicketHistory
    fields = ('ticket_state', 'created_at')
    readonly_fields = ('ticket_state', 'created_at')
    extra = 0

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False



@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    readonly_fields = ('state',)
    inlines = [TicketHistoryInlineAdmin, ]
