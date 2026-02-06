import random
import threading
import time
from collections import defaultdict

GRID_SIZE = 10
MAX_COUNTRIES = 5
MAX_SOLDIERS_PER_COUNTRY = 10
MAX_TANKS_PER_COUNTRY = 3

class Unit:
    def __init__(self, unit_id, country, country_id):
        self.id = unit_id
        self.country = country
        self.country_id = country_id
        self.x = random.randint(0, GRID_SIZE - 1)
        self.y = random.randint(0, GRID_SIZE - 1)
        self.active = True

    def move(self):
        if not self.active:
            return

        possible_moves = []
        if self.x > 0:
            possible_moves.append((-1, 0))
        if self.x < GRID_SIZE - 1:
            possible_moves.append((1, 0))
        if self.y > 0:
            possible_moves.append((0, -1))
        if self.y < GRID_SIZE - 1:
            possible_moves.append((0, 1))

        if not possible_moves:
            return # No valid moves

        dx, dy = random.choice(possible_moves)
        self.x += dx
        self.y += dy

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id}) @ ({self.x}, {self.y})"

class Soldier(Unit):
    pass

class Tank(Unit):
    pass

class Battlefield:
    def __init__(self):
        self.countries = {}
        self.units = []
        self.country_id_map = {}
        self.next_country_id = 1
        self.lock = threading.Lock()
        self._simulation_thread = None
        self.simulation_running = False

    def add_country(self, name, soldiers, tanks):
        with self.lock:
            if len(self.countries) >= MAX_COUNTRIES:
                raise ValueError("Maximum number of countries reached.")
            if name in self.countries:
                raise ValueError(f"Country '{name}' already exists.")
            if not (0 < soldiers <= MAX_SOLDIERS_PER_COUNTRY):
                raise ValueError(f"Soldier count must be between 1 and {MAX_SOLDIERS_PER_COUNTRY}.")
            if not (0 <= tanks <= MAX_TANKS_PER_COUNTRY):
                 raise ValueError(f"Tank count must be between 0 and {MAX_TANKS_PER_COUNTRY}.")

            country_id = self.next_country_id
            self.country_id_map[name] = country_id
            self.next_country_id += 1

            self.countries[name] = {'soldiers': [], 'tanks': []}
            
            for i in range(soldiers):
                soldier = Soldier(f"{name}-S{i+1}", name, country_id)
                self.units.append(soldier)
                self.countries[name]['soldiers'].append(soldier)

            for i in range(tanks):
                tank = Tank(f"{name}-T{i+1}", name, country_id)
                self.units.append(tank)
                self.countries[name]['tanks'].append(tank)
        
        return True

    def _resolve_collisions(self):
        grid = defaultdict(list)
        for unit in self.units:
            if unit.active:
                grid[(unit.x, unit.y)].append(unit)
        for pos, occupants in grid.items():
            if len(occupants) < 2:
                continue
            first_country = occupants[0].country
            if all(u.country == first_country for u in occupants):
                continue
            soldiers = [u for u in occupants if isinstance(u, Soldier)]
            tanks = [u for u in occupants if isinstance(u, Tank)]
            if len(tanks) > 1:
                for i in range(len(tanks)):
                    for j in range(i + 1, len(tanks)):
                        if tanks[i].country != tanks[j].country:
                            tanks[i].active = False
                            tanks[j].active = False
            if tanks and soldiers:
                for tank in tanks:
                    for soldier in soldiers:
                        if tank.country != soldier.country:
                            soldier.active = False
            if not tanks and len(soldiers) > 1:
                for i in range(len(soldiers)):
                    for j in range(i + 1, len(soldiers)):
                        if soldiers[i].country != soldiers[j].country:
                            soldiers[i].active = False
                            soldiers[j].active = False
        self.units = [u for u in self.units if u.active]
        for name in list(self.countries.keys()):
            self.countries[name]['soldiers'] = [s for s in self.countries[name]['soldiers'] if s.active]
            self.countries[name]['tanks'] = [t for t in self.countries[name]['tanks'] if t.active]

    def run_step(self):
        with self.lock:
            self._move_all_units()
            self._resolve_collisions()
            self._remove_defeated_countries()

    def _move_all_units(self):
        for unit in self.units:
            unit.move()

    def _remove_defeated_countries(self):
        defeated_countries = [
            name for name, units in self.countries.items()
            if not units['soldiers'] and not units['tanks']
        ]
        for name in defeated_countries:
            del self.countries[name]
            del self.country_id_map[name]

    def get_state(self):
        with self.lock:
            return {
                name: {'soldiers': len(units['soldiers']), 'tanks': len(units['tanks'])}
                for name, units in self.countries.items()
            }

    def print_grid(self):
        grid = [['.' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        for unit in self.units:
            if unit.active:
                symbol = 's' if isinstance(unit, Soldier) else 't'
                grid[unit.y][unit.x] = f"{symbol}{unit.country_id}"
        
        print("\n" + "="*30)
        for row in grid:
            print(" ".join(f"{cell:^3}" for cell in row))
        print("="*30)
        if self.countries:
            print("Legend: " + ", ".join(f"{name}={self.country_id_map[name]}" for name in self.countries))

    def _simulation_loop(self):
        while self.simulation_running:
            self.run_step()
            self.print_grid()
            time.sleep(1)
        self._simulation_thread = None

    def start_simulation(self):
        with self.lock:
            if self.simulation_running:
                return "Simulation is already running."
            if len(self.countries) < 2:
                return "Cannot start simulation with fewer than two countries."
            self.simulation_running = True
            self._simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
            self._simulation_thread.start()
            return "Simulation started."

    def stop_simulation(self):
        with self.lock:
            if not self.simulation_running:
                return "Simulation is not running."
            self.simulation_running = False
        if self._simulation_thread:
            self._simulation_thread.join()
        return "Simulation stopped."

    def restart_simulation(self):
        self.stop_simulation()
        with self.lock:
            self.countries.clear()
            self.units.clear()
            self.country_id_map.clear()
            self.next_country_id = 1
        return "Simulation restarted and battlefield cleared."

battlefield = Battlefield()
