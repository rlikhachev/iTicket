from django.db import models
from user.models import User
from django_fsm import FSMField, transition
from django.db.models.signals import post_save
from ..helpers import get_assigner


STATES = (
    ('new', 'Новый'),
    ('assigned', 'Назначен'),
    ('processed', 'Обрабатывается'),
    ('done', 'Выполнен'),
    ('close', 'Закрыт'),
    ('canceled', 'Отменен'),
    ('reopen', 'Переоткрыт')
)


class Ticket(models.Model):
    title = models.CharField(max_length=1024, verbose_name='Заголовок тикета')
    description = models.TextField(verbose_name='Описание', default='')
    state = FSMField(default='new', choices=STATES, verbose_name='Состояние тикета')
    author = models.ForeignKey(User, verbose_name='Автор', related_name='author', on_delete=models.CASCADE, blank=True, null=True)
    actor = models.ForeignKey(User, verbose_name='Исполнитель', related_name='actor', on_delete=models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def __str__(self):
        return self.title

    def user_can_process(self):
        return False if self.actor.actor.filter(state='processed').exists() else True

    @transition(field=state, source=['new', 'reopen'], target='assigned')
    def assigned(self):
        pass

    @transition(field=state, source='assigned', target='processed', conditions=[user_can_process])
    def processed(self):
        pass

    @transition(field=state, source='processed', target='done')
    def done(self):
        pass

    @transition(field=state, source='processed', target='canceled')
    def canceled(self):
        pass

    @transition(field=state, source='done', target='close')
    def closed(self):
        pass

    @transition(field=state, source=['done', 'canceled'], target='reopen')
    def reopen(self):
        pass

    class Meta:
        verbose_name = 'Тикет'
        verbose_name_plural = 'Тикеты'
        permissions = (
            ("can_view_statistic", "Может просматривать статистику по тикетам"),
            ("can_create", "Может создавать тикеты"),
            ("can_view", "Может просматривать тикет"),
            ("close_reopen", "Может закрыть/переоткрыть тикет"),
            ("proceed_done_cancel", "Может обрабатывать/завершать/отменять тикет"),
        )


post_save.connect(receiver=get_assigner, sender=Ticket)


class TicketHistory(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='history', verbose_name='Тикет', on_delete=models.CASCADE, null=True)
    ticket_state = models.CharField(max_length=255, verbose_name='Состояния тикета')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f'{self.ticket} {self.created_at} '

    class Meta:
        verbose_name = 'История'
        verbose_name_plural = 'История'

