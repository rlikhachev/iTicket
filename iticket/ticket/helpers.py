from user.models import User
from rest_framework.permissions import BasePermission


def get_assigner(sender, instance, created, **kwargs):
    from .models.ticket import TicketHistory
    last_history = TicketHistory.objects.filter(ticket_id=instance.id).order_by('-created_at').first()
    make_history = False
    if created:
        make_history = True
    else:
        if last_history:
            if last_history.ticket_state == instance.state:
                pass
            else:
                make_history = True
    if make_history:
        TicketHistory.objects.create(ticket_id=instance.id, ticket_state=instance.state)
    if not instance.actor or instance.state == 'reopen':
        users = User.objects.exclude(is_superuser=True).exclude(id=instance.author.id)
        tmp = []
        for user in users:
            assigned = user.actor.filter(state='assigned').count()
            processed = user.actor.filter(state='processed').count()
            tmp.append((assigned+processed, user))

        tmp.sort(key=lambda x: x[0])
        try:
            res = tmp[0][1]
        except IndexError:
            res = users.first()
        instance.actor = res
        instance.assigned()
        instance.save()


def get_permissions():
    from django.contrib.auth.models import Permission
    return Permission.objects.filter(content_type__app_label='ticket', codename__in=['can_view_statistic',
                                     'can_create', 'can_view', 'close_reopen', 'proceed_done_cancel'])


class CanViewStatistic(BasePermission):

    def has_permission(self, request, view):
        permission = get_permissions().filter(codename='can_view_statistic').first()
        if permission in request.user.user_permissions.all():
            return True
        else:
            return False

