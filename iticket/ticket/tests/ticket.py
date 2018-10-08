from django.test import TestCase
from ticket.models import Ticket
from user.models import User
from rest_framework.test import APIClient
from ticket.helpers import get_permissions
from django.utils import timezone


class TicketTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.users_credentials = {}
        for i in range(1,5):
            self.users_credentials.update({i: {'username': f'test_user{i}', 'password': f'testpsswd{i}'}})
        for key, value in self.users_credentials.items():
            User.objects.create_user(**value)
        User.objects.filter(id=1).first().user_permissions.add(get_permissions().filter(codename='can_view_statistic').first())

    def test_ticket_workflow(self):
        # login for users
        user1 = APIClient()
        login_response = user1.post('/auth/login/', self.users_credentials[1])
        user1.credentials(HTTP_AUTHORIZATION='Token ' + login_response.data['token'])

        user2 = APIClient()
        log_user2 = user2.post('/auth/login/', self.users_credentials[2])
        user2.credentials(HTTP_AUTHORIZATION='Token ' + log_user2.data['token'])

        user3 = APIClient()
        log_user3 = user3.post('/auth/login/', self.users_credentials[3])
        user3.credentials(HTTP_AUTHORIZATION='Token ' + log_user3.data['token'])

        task_from_user1 = {}
        for i in range(1, 8):
            task_from_user1.update({
                i: {
                'title': f'task {i} from user1',
                'description': f'description task {i} from user1'
                }
            })

        for k, v in task_from_user1.items():
            response = user1.post('/api/tickets/', v)
            self.assertTrue(response.status_code == 201 and response.data)

        tickets = Ticket.objects.all()
        tickets_list = []
        for user in User.objects.exclude(id=1):
            tickets_list.append(tickets.filter(actor=user.id).count())

        for index in range(0, len(tickets_list)-1):
            diff = tickets_list[index] - tickets_list[index+1]
            self.assertLess(diff, 2, msg='Разница по количеству назначеных тикетов больше 1')

        # test take to process

        user2_tickets = list(tickets.filter(actor=2))
        for ticket in user2_tickets:
            # take 1 to process
            if user2_tickets.index(ticket) == 0:
                response = user2.post(f'/api/tickets/{ticket.id}/process/')
                self.assertEqual(response.status_code, 200)
            # try take rest tickets to process too
            else:
                response = user2.post(f'/api/tickets/{ticket.id}/process/')
                self.assertNotEqual(response.status_code, 200)

        # test cant close not processed ticket (2)
        user2_assigned_ticket = tickets.filter(actor=2, state='assigned').first()
        response = user2.post(f'/api/tickets/{user2_assigned_ticket.id}/close/')
        self.assertNotEqual(response.status_code, 200)

        # test user can cancel one and then take other, set it done

        # cancel processed (1)
        user2_processed_ticket = tickets.filter(actor=2, state='processed').first()
        response = user2.post(f'/api/tickets/{user2_processed_ticket.id}/cancel/')
        self.assertEqual(response.status_code, 200)

        # try canceled set to reopen not by author (1)
        response = user2.post(f'/api/tickets/{user2_processed_ticket.id}/reopen/')
        self.assertNotEqual(response.status_code, 200)

        # set another to processed (2)
        response = user2.post(f'/api/tickets/{user2_assigned_ticket.id}/process/')
        self.assertEqual(response.status_code, 200)

        # set another to processed (2)
        response = user2.post(f'/api/tickets/{user2_assigned_ticket.id}/done/')
        self.assertEqual(response.status_code, 200)

        # try done set to close (2) by actor
        response = user2.post(f'/api/tickets/{user2_assigned_ticket.id}/close/')
        self.assertNotEqual(response.status_code, 200)

        # try done set to close (2) by author
        response = user1.post(f'/api/tickets/{user2_assigned_ticket.id}/close/')
        self.assertEqual(response.status_code, 200)

        # try canceled set to close (1)
        response = user2.post(f'/api/tickets/{user2_processed_ticket.id}/close/')
        self.assertNotEqual(response.status_code, 200)

        # try to reopen assigned by author (user 3)
        user3_assigned_ticket = tickets.filter(actor=3, state='assigned').first()
        response = user1.post(f'/api/tickets/{user3_assigned_ticket.id}/reopen/')
        self.assertNotEqual(response.status_code, 200)

        # try to reopen canceled by author (1)
        response = user1.post(f'/api/tickets/{user2_processed_ticket.id}/reopen/')
        self.assertEqual(response.status_code, 200)

        # check amount of history items (1)
        ticket1_history_items_count = user2_processed_ticket.history.all().count()
        self.assertEqual(ticket1_history_items_count, 6)

        # try do anything by user not signed to tickets

        for ticket in user2_tickets:
            response = user3.post(f'/api/tickets/{ticket.id}/process/')
            self.assertNotEqual(response.status_code, 200)
            response = user3.post(f'/api/tickets/{ticket.id}/cancel/')
            self.assertNotEqual(response.status_code, 200)
            response = user3.post(f'/api/tickets/{ticket.id}/done/')
            self.assertNotEqual(response.status_code, 200)
            response = user3.post(f'/api/tickets/{ticket.id}/close/')
            self.assertNotEqual(response.status_code, 200)
            response = user3.post(f'/api/tickets/{ticket.id}/reopen/')
            self.assertNotEqual(response.status_code, 200)

        date_to = timezone.now() + timezone.timedelta(days=1)

        response = user1.get(f'/api/statistic/', {'date_to': date_to.strftime('%d.%m.%Y')})
        self.assertEqual(response.status_code, 200)

        date_to = timezone.now() - timezone.timedelta(days=1)
        response = user1.get(f'/api/statistic/', {'date_to': date_to.strftime('%d.%m.%Y')})
        self.assertEqual(response.status_code, 200)

        response = user2.get(f'/api/statistic/', {'date_to': date_to.strftime('%d.%m.%Y')})
        self.assertNotEqual(response.status_code, 200)
