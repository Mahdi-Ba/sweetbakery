from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.
from apps.file.api.serializer import FileSerializer
from apps.file.forms import FileForm
from apps.file.models import File
from apps.general.api.serializer import *
from apps.general.models import State

from rest_framework.permissions import AllowAny

class FileUploadView(APIView):
    def post(self, request):
        serializer = FileSerializer(data=request.FILES)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'success': True, 'data': serializer.data, 'message': ''})
        else:
            return Response({'success': False, 'data': [], 'message': 'file is not valid'})
