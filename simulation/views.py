from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from .logic import battlefield
from .serializers import AddCountrySerializer, BattleStateSerializer

class AddCountryView(APIView):
    serializer_class = AddCountrySerializer

    @extend_schema(
        request=AddCountrySerializer,
        responses={200: {'description': 'Country added successfully.'}}
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                battlefield.add_country(**serializer.validated_data)
                return Response({'status': 'success', 'message': f'Country {serializer.validated_data["name"]} added.'})
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BattleStateView(APIView):
    serializer_class = BattleStateSerializer
    
    @extend_schema(
        responses={200: BattleStateSerializer}
    )
    def get(self, request):
        state = battlefield.get_state()
        serializer = self.serializer_class(data={'countries': state})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

class StartSimulationView(APIView):
    @extend_schema(
        responses={
            200: {'description': 'Simulation started.'},
            400: {'description': 'Simulation is already running or no countries.'}
        }
    )
    def post(self, request):
        message = battlefield.start_simulation()
        if "started" in message:
            return Response({'status': 'success', 'message': message})
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

class StopSimulationView(APIView):
    @extend_schema(
        responses={
            200: {'description': 'Simulation stopped.'},
            400: {'description': 'Simulation is not running.'}
        }
    )
    def post(self, request):
        message = battlefield.stop_simulation()
        if "stopped" in message:
            return Response({'status': 'success', 'message': message})
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

class RestartSimulationView(APIView):
    @extend_schema(
        responses={200: {'description': 'Simulation restarted and battlefield cleared.'}}
    )
    def post(self, request):
        message = battlefield.restart_simulation()
        return Response({'status': 'success', 'message': message})
