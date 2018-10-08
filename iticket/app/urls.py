from django.contrib import admin
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view
from rest_framework import routers
from ticket.views.ticket import TicketViewSet, TicketChangeStateViewSet, TicketStatisticAPIView
from user.views import Logout, Login


schema_view = get_swagger_view(title='iTicket API')


router = routers.DefaultRouter()
router.register('tickets', TicketViewSet)
router.register('tickets', TicketChangeStateViewSet)
router.register('statistic', TicketStatisticAPIView)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', schema_view),
    path('auth/login/', Login.as_view()),
    path('auth/logout/', Logout.as_view()),
    path('api/', include(router.urls)),
]

