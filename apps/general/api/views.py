from datetime import datetime, timedelta
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.general.api.serializer import *
from apps.general.models import State
from rest_framework.permissions import AllowAny


@permission_classes((AllowAny,))
class StateList(APIView):
    @swagger_auto_schema(operation_description="country list", responses={200: StateSerializer(many=False)})
    def get(self, request):
        state = State.objects.filter().all()
        serializer = StateSerializer(state, many=True)
        return Response({'success': True, 'data': serializer.data, 'message': ''})


@permission_classes((AllowAny,))
class ProvincesListByState(APIView):
    def get(self, request, pk):
        provinces = Province.objects.filter(state__id=pk)
        serializer = ProvinceSerializer(provinces, many=True)
        return Response({'success': True, 'data': serializer.data, 'message': ''})


@permission_classes((AllowAny,))
class LocationListByProvince(APIView):
    def get(self, request, pk):
        location = Location.objects.filter(province_id=pk)
        serializer = LocationSerializer(location, many=True)
        return Response({'success': True, 'data': serializer.data, 'message': ''})


@permission_classes((AllowAny,))
class SchedulingListByLocation(APIView):
    def get(self, request, pk):
        scheduling = Scheduling.objects.filter(location_id=pk, is_enable=True,
                                               deliver_date_time__gte=datetime.date(datetime.now() + timedelta(days=1)))
        serializer = SchedulingSerializer(scheduling, many=True)
        return Response({'success': True, 'data': serializer.data, 'message': ''})


@permission_classes((AllowAny,))
class SchedulingScriptLocation(APIView):
    def get(self, request):
        """
        select mp.id as product_id,mp.name as product_name,sum(market_invoice.quantity) total,gl.title as location,gp.title as city
             ,gs.deliver_date_time from market_invoice inner join market_order mo on mo.id = market_invoice.order_id
        inner join general_scheduling gs on gs.id = mo.scheduling_id
        inner join market_product mp on mp.id = market_invoice.product_id
        inner join general_location gl on gl.id = gs.location_id
        inner join general_province gp on gl.province_id = gp.id
        group by product_id,location
        """



        """
        select mp.id as product_id,mp.name as product_name,sum(market_invoice.quantity) total
             ,gs.deliver_date_time from market_invoice inner join market_order mo on mo.id = market_invoice.order_id
        inner join general_scheduling gs on gs.id = mo.scheduling_id
        inner join market_product mp on mp.id = market_invoice.product_id
        inner join general_location gl on gl.id = gs.location_id
        inner join general_province gp on gl.province_id = gp.id
        group by product_id,name
        
        """
        from datetime import datetime, timedelta
        schedulings = Scheduling.objects.all()
        for item in schedulings:
            weeks = 2
            for i in range(1, 36):
                increase = weeks * i
                Scheduling.objects.create(
                    deliver_date_time=item.deliver_date_time + timedelta(weeks=increase),
                    deliver_end_date_time=item.deliver_end_date_time,
                    location=item.location,
                    is_enable=False

                )
