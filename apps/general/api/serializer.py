from rest_framework import serializers

from apps.general.models import State, Province, Location, Scheduling


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = [
            'id', 'title','shipping_cost'
        ]


class ProvinceSerializer(serializers.ModelSerializer):
    state = StateSerializer(read_only=True, many=False)
    class Meta:
        model = Province
        fields = '__all__'



class LocationSerializer(serializers.ModelSerializer):
    province = ProvinceSerializer(read_only=True, many=False)

    class Meta:
        model = Location
        fields = '__all__'



class SchedulingSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True, many=False)

    class Meta:
        model = Scheduling
        fields = '__all__'




