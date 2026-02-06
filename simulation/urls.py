from django.urls import path
from .views import AddCountryView, BattleStateView, StartSimulationView, StopSimulationView, RestartSimulationView

urlpatterns = [
    path('countries', AddCountryView.as_view(), name='add_country'),
    path('state', BattleStateView.as_view(), name='get_battle_state'),
    path('start', StartSimulationView.as_view(), name='start_simulation'),
    path('stop', StopSimulationView.as_view(), name='stop_simulation'),
    path('restart', RestartSimulationView.as_view(), name='restart_simulation'),
]
