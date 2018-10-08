from rest_framework import viewsets
from ..models.ticket import Ticket, STATES
from ..serializers import TicketSerializer, TicketIdSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django_fsm import TransitionNotAllowed
from rest_framework import mixins
from django.utils import timezone
from ..filters.ticket import TicketFilter
from ..helpers import CanViewStatistic
from django.conf import settings
from pytz import timezone as tz


class TicketViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        """
        create and return created ticket
        """
        user = request.user
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            ticket = Ticket(
                title=serializer.validated_data['title'],
                description=serializer.validated_data['description'],
                author=user,
            )
            ticket.save()
            serializer = TicketSerializer(ticket)
            return Response(serializer.data, status=201)
        else:
            return Response('Not created', status=502)

    def retrieve(self, request, pk=None, **kwargs):
        """
        return ticket by pk
        """
        user = request.user
        if user.is_superuser:
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(author=user)
        ticket = get_object_or_404(queryset, pk=pk)
        serializer = TicketSerializer(ticket)
        return Response(serializer.data)


class TicketChangeStateViewSet(viewsets.GenericViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketIdSerializer
    permission_classes = (IsAuthenticated,)

    @action(methods=['post'], detail=True)
    def process(self, request, pk=None, **kwargs):
        """
        set proceed ticket by pk
        """
        user = request.user
        queryset = self.queryset.filter(actor=user)
        ticket = get_object_or_404(queryset, pk=pk)
        try:
            ticket.processed()
        except TransitionNotAllowed:
            return Response('Not allowed now. Possible you are already have a ticket in process.', status=502)
        ticket.save()
        serializer = TicketIdSerializer(ticket)
        return Response(serializer.data)

    @action(methods=['post'], detail=True)
    def cancel(self, request, pk=None, **kwargs):
        """
        set cancel ticket by pk
        """
        user = request.user
        queryset = self.queryset.filter(actor=user)
        ticket = get_object_or_404(queryset, pk=pk)
        try:
            ticket.canceled()
        except TransitionNotAllowed:
            return Response('Method not alowed', status=502)
        ticket.save()
        serializer = TicketIdSerializer(ticket)
        return Response(serializer.data)

    @action(methods=['post'], detail=True)
    def done(self, request, pk=None, **kwargs):
        """
        set done ticket by pk
        """
        user = request.user
        queryset = self.queryset.filter(actor=user)
        ticket = get_object_or_404(queryset, pk=pk)
        try:
            ticket.done()
        except TransitionNotAllowed:
            return Response('Method not alowed', status=502)
        ticket.save()
        serializer = TicketIdSerializer(ticket)
        return Response(serializer.data)

    @action(methods=['post'], detail=True)
    def reopen(self, request, pk=None, **kwargs):
        """
        set reopen ticket by pk
        """
        user = request.user
        queryset = self.queryset.filter(author=user)
        ticket = get_object_or_404(queryset, pk=pk)
        try:
            ticket.reopen()
        except TransitionNotAllowed:
            return Response('Method not alowed', status=502)
        ticket.save()
        serializer = TicketIdSerializer(ticket)
        return Response(serializer.data)

    @action(methods=['post'], detail=True)
    def close(self, request, pk=None, **kwargs):
        """
        set reopen ticket by pk
        """
        user = request.user
        queryset = self.queryset.filter(author=user)
        ticket = get_object_or_404(queryset, pk=pk)
        try:
            ticket.closed()
        except TransitionNotAllowed:
            return Response('Method not alowed', status=502)
        ticket.save()
        serializer = TicketIdSerializer(ticket)
        return Response(serializer.data)


class TicketStatisticAPIView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = (IsAuthenticated, CanViewStatistic)
    filter_class = TicketFilter

    def list(self, request, *args, **kwargs):
        """
        Get statistic info about tickets count per ACTOR (if given) and per UPDATED_AT date range (if given).
        Data divided per ticket.state
        """
        actor = request.GET.get('actor', None)

        date_from = request.GET.get('date_from', None)
        date_from = timezone.datetime.strptime(date_from, '%d.%m.%Y')if date_from  \
                    else timezone.datetime(day=1, month=1, year=2018)
        date_from = date_from.replace(tzinfo=tz(settings.TIME_ZONE))

        date_to = request.GET.get('date_to', None)
        date_to = timezone.datetime.strptime(date_to, '%d.%m.%Y') if date_to else timezone.now()
        date_to = date_to.replace(tzinfo=tz(settings.TIME_ZONE))
        qs = self.queryset.filter(updated_at__range=(date_from, date_to))
        if actor:
            qs = self.queryset.filter(actor=actor)

        if qs.count() == 0:
            return Response('No data for given params (id: {}, date_from: {}, date_to: {})'.
                            format(actor, date_from.strftime('%d.%m.%Y'), date_to.strftime('%d.%m.%Y')))

        tickets_count = {}

        for state, state_title in STATES:
            tickets_count.update(
                {state: {
                    'title': state_title,
                    'count': qs.filter(state=state).count()
                }
                })

        data = {
            'actor': actor if actor else 'all',
            'from date': date_from.strftime('%d.%m.%Y'),
            'to date': date_to.strftime('%d.%m.%Y'),
            'tickets': tickets_count
        }
        # print(data)
        return Response(data)
