from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout, login
from user.models import User


class Logout(APIView):

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        # user = self.queryset.get(pk=request.user.id)
        try:
            request.user.auth_token.delete()
        except:
            pass
        logout(request)
        return Response({'detail': 'Logout successfull'})


class Login(ObtainAuthToken):
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        login(request, user)
        return Response({'token': token.key})
