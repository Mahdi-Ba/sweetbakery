from django.utils.translation import gettext as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.wallets.api.serializer import WalletSerializer
from apps.wallets.models import Wallet


class WalletList(APIView):
    @swagger_auto_schema(operation_description="wallet of user", responses={200: WalletSerializer(many=False)})
    def get(self, request):
        wallet = Wallet.objects.filter(user=request.user).first()
        return Response(
            {'success': True, 'message': _("mission accomplished"), 'dev_message': 'wallet of user who login',
             'data': WalletSerializer(wallet, many=False).data})


class Deposit(APIView):
    def post(self, request):
        pass


class WithDraw(APIView):
    def post(self, request):
        pass
