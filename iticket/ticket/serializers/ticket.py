from rest_framework import serializers
from ..models import Ticket


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ('id', 'title', 'description', 'state', 'author', 'actor')
        read_only_fields = ('state', 'author', 'actor')


class TicketIdSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ('id',)


class TicketStatisticSerializer(serializers.Serializer):
    user = serializers.IntegerField(required=True)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    ticket_data = serializers.JSONField(required=False)

    class Meta:
        fields = ('user', 'date_from', 'date_to')



