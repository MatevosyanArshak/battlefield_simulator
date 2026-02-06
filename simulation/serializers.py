from rest_framework import serializers

class AddCountrySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    soldiers = serializers.IntegerField(min_value=1, max_value=10)
    tanks = serializers.IntegerField(min_value=0, max_value=3)

class CountryStateSerializer(serializers.Serializer):
    soldiers = serializers.IntegerField()
    tanks = serializers.IntegerField()

class BattleStateSerializer(serializers.Serializer):
    countries = serializers.DictField(child=CountryStateSerializer())
