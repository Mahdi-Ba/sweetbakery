import base64
import hashlib
import uuid
from django.core.files.base import ContentFile
from drf_yasg.utils import swagger_auto_schema
from .serializers import UserSerializer, UserFullSerializer, LoginSerializer

from .trait import imageConvertor, OneTimePassMixin, jWTMixin
from .userservice import JWTSimpleUserService
from ..models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_jwt.settings import api_settings
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.db.models import Q
from django.core.cache import cache
from django.utils.translation import gettext as _

from ...wallets.models import Wallet




class LoginRigisterRateThrottle(UserRateThrottle):
    rate = '4/minute'


@permission_classes((AllowAny,))
class StaticLogin(APIView):
    throttle_classes = [LoginRigisterRateThrottle]

    def post(self, request):
        login_serializer = LoginSerializer(data=request.data)
        if not login_serializer.is_valid():
            return Response({"success": False, 'dev_message': 'wrong functionality'
                                , "message": _('your information is not correct'),
                             'data': {'messages': login_serializer.errors}},
                            status=status.HTTP_400_BAD_REQUEST)
        jwt_simple = JWTSimpleUserService().check_user_authenticate(request.data['email'], request.data['password'])
        if jwt_simple.user:
            return Response({
                'success': True,
                'data': {
                    'token': jwt_simple.get_token(),
                    'user_info': UserSerializer(jwt_simple.user).data

                },
                'message': _('welcome to T_Boof'),
                'dev_message': 'token generate'

            })
        else:
            return Response({
                'success': False,
                'message': _("Incorrect Info"),
                'dev_message': 'mistake user and pass'
            }, status=status.HTTP_401_UNAUTHORIZED)


@permission_classes((AllowAny,))
class Register(APIView,jWTMixin, OneTimePassMixin,):
    @swagger_auto_schema(operation_description="register new user", request_body=UserFullSerializer)
    def post(self, request):
        request.data['mobile'] = request.data['mobile']
        serializer = UserFullSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data['password'])
            user.save()
            return Response({'success': True, 'user': serializer.data,'token':self.getToken(user), 'message': 'user register successfully'})
        else:
            return Response(
                {'success': False, 'message': _('warning! error occurred'), 'data': {'messages': serializer.errors}},
                status.HTTP_400_BAD_REQUEST)





class UserList(APIView):
    @swagger_auto_schema(responses={200: UserSerializer(many=False)})
    def get(self, request):
        serializer = UserSerializer(instance=request.user)
        return Response({"success": True, "message": _('mission accomplished'), 'dev_message': 'done',
                         'data': serializer.data})

    @swagger_auto_schema(request_body=UserSerializer, responses={200: UserSerializer(many=False)})
    def put(self, request):
        user = User.objects.get(email=request.user)
        if request.data.get('avatar', False):
            if user.avatar is not None:
                user.avatar.delete()
            request.data['avatar'] = imageConvertor(request.data.pop('avatar'))[0]

        serializer = UserSerializer(data=request.data, instance=user)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": _('mission accomplished'), 'dev_message': 'done',
                             'data': serializer.data})
        else:
            return Response({"success": False, 'dev_message': 'wrong functionality'
                                , "message": _('warning! error occurred'), 'data': {'messages': serializer.errors}},
                            status=status.HTTP_400_BAD_REQUEST)


