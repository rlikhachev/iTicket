from django.contrib import admin
from ..models import Ticket, TicketHistory



@admin.register(TicketHistory)
class TicketHistoryAdmin(admin.ModelAdmin):
    pass


class TicketHistoryInlineAdmin(admin.TabularInline):
    model = TicketHistory
    fields = ('ticket_state', 'created_at')
    readonly_fields = ('ticket_state', 'created_at')



@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    readonly_fields = ('state',)
    inlines = [TicketHistoryInlineAdmin, ]
