from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch

from .logic import Battlefield, Soldier, Tank, battlefield

class BattlefieldLogicTests(TestCase):
    def setUp(self):
        # We create a new Battlefield instance for each test to ensure isolation
        self.bf = Battlefield()

    def test_add_country_success(self):
        self.bf.add_country("CountryA", soldiers=5, tanks=2)
        self.assertIn("CountryA", self.bf.countries)
        self.assertEqual(len(self.bf.countries["CountryA"]["soldiers"]), 5)
        self.assertEqual(len(self.bf.countries["CountryA"]["tanks"]), 2)
        self.assertEqual(len(self.bf.units), 7)

    def test_add_country_exceeds_max(self):
        for i in range(5):
            self.bf.add_country(f"Country{i}", soldiers=1, tanks=1)
        with self.assertRaises(ValueError, msg="Maximum number of countries reached."):
            self.bf.add_country("CountryF", soldiers=1, tanks=1)

    def test_add_country_duplicate_name(self):
        self.bf.add_country("CountryA", soldiers=1, tanks=1)
        with self.assertRaises(ValueError, msg="Country 'CountryA' already exists."):
            self.bf.add_country("CountryA", soldiers=1, tanks=1)

    def test_add_country_invalid_units(self):
        with self.assertRaises(ValueError):
            self.bf.add_country("CountryA", soldiers=11, tanks=1) # Too many soldiers
        with self.assertRaises(ValueError):
            self.bf.add_country("CountryB", soldiers=1, tanks=4) # Too many tanks
        with self.assertRaises(ValueError):
            self.bf.add_country("CountryC", soldiers=0, tanks=0) # No units

    def test_no_friendly_fire(self):
        self.bf.add_country("CountryA", soldiers=2, tanks=0)
        soldier1, soldier2 = self.bf.units
        # Place them on the same cell
        soldier1.x, soldier1.y = 5, 5
        soldier2.x, soldier2.y = 5, 5
        
        self.bf._resolve_collisions()
        self.assertTrue(soldier1.active)
        self.assertTrue(soldier2.active)
        self.assertEqual(len(self.bf.units), 2)

    def test_enemy_collision_soldier_vs_soldier(self):
        self.bf.add_country("CountryA", soldiers=1, tanks=0)
        self.bf.add_country("CountryB", soldiers=1, tanks=0)
        soldier1, soldier2 = self.bf.units
        soldier1.x, soldier1.y = 5, 5
        soldier2.x, soldier2.y = 5, 5

        self.bf._resolve_collisions()
        self.assertFalse(soldier1.active)
        self.assertFalse(soldier2.active)

    def test_enemy_collision_soldier_vs_tank(self):
        self.bf.add_country("CountryA", soldiers=1, tanks=0)
        self.bf.add_country("CountryB", soldiers=0, tanks=1)
        soldier, tank = self.bf.units[0], self.bf.units[1]
        soldier.x, soldier.y = 5, 5
        tank.x, tank.y = 5, 5

        self.bf._resolve_collisions()
        self.assertFalse(soldier.active)
        self.assertTrue(tank.active)

    def test_enemy_collision_tank_vs_tank(self):
        self.bf.add_country("CountryA", soldiers=0, tanks=1)
        self.bf.add_country("CountryB", soldiers=0, tanks=1)
        tank1, tank2 = self.bf.units
        tank1.x, tank1.y = 5, 5
        tank2.x, tank2.y = 5, 5

        self.bf._resolve_collisions()
        self.assertFalse(tank1.active)
        self.assertFalse(tank2.active)

    def test_remove_defeated_country(self):
        self.bf.add_country("CountryA", soldiers=1, tanks=0)
        self.bf.add_country("CountryB", soldiers=0, tanks=1)
        soldier, tank = self.bf.units[0], self.bf.units[1]
        soldier.x, soldier.y = 5, 5
        tank.x, tank.y = 5, 5

        self.bf.run_step() # move, collide, and remove
        self.assertNotIn("CountryA", self.bf.countries)
        self.assertIn("CountryB", self.bf.countries)

    def test_unit_move_in_corner(self):
        unit = Soldier("test", "A", 1)
        unit.x, unit.y = 0, 0
        
        # In a corner, a unit should only have 2 possible moves
        with patch('random.choice', return_value=(1, 0)) as mock_choice:
            unit.move()
            self.assertEqual(len(mock_choice.call_args[0][0]), 2)


class SimulationAPITests(APITestCase):
    def setUp(self):
        # Reset the global battlefield instance before each test
        battlefield.restart_simulation()

    def test_add_country_api(self):
        url = "/api/countries"
        data = {"name": "CountryA", "soldiers": 5, "tanks": 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("CountryA", battlefield.countries)

    def test_add_country_api_invalid(self):
        url = "/api/countries"
        data = {"name": "CountryA", "soldiers": 99, "tanks": 2} # Invalid soldier count
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_state_api(self):
        battlefield.add_country("CountryA", soldiers=5, tanks=2)
        url = "/api/state"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["countries"]["CountryA"]["soldiers"], 5)

    def test_start_simulation_api(self):
        # Fails with < 2 countries
        battlefield.add_country("CountryA", soldiers=1, tanks=1)
        response = self.client.post("/api/start")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("fewer than two", response.data["error"])

        # Succeeds with >= 2 countries
        battlefield.add_country("CountryB", soldiers=1, tanks=1)
        response = self.client.post("/api/start")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(battlefield.simulation_running)

        # Fails if already running
        response = self.client.post("/api/start")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already running", response.data["error"])

    def test_stop_simulation_api(self):
        # Fails if not running
        response = self.client.post("/api/stop")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Succeeds if running
        battlefield.add_country("CountryA", soldiers=1, tanks=1)
        battlefield.add_country("CountryB", soldiers=1, tanks=1)
        battlefield.start_simulation()
        response = self.client.post("/api/stop")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(battlefield.simulation_running)

    def test_restart_simulation_api(self):
        battlefield.add_country("CountryA", soldiers=1, tanks=1)
        battlefield.start_simulation()
        
        url = "/api/restart"
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(battlefield.simulation_running)
        self.assertEqual(len(battlefield.countries), 0)
        self.assertEqual(len(battlefield.units), 0)
