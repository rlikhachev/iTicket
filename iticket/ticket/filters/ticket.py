from django_filters import rest_framework as filters
from ..models import Ticket


class TicketFilter(filters.FilterSet):
    actor = filters.NumberFilter(field_name='actor__id')
    date_from = filters.DateFilter(field_name='updated_at')
    date_to = filters.DateFilter(field_name='updated_at')

    class Meta:
        model = Ticket
        fields = ('actor', 'date_from', 'date_to')
