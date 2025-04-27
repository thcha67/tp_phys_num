import json
import time
from config import *
import subprocess
import os
import sys
import babyfoot_table_vpython

STRATEGY_ENUM = (
    "gk_all_time",
    "opportunistic_attack",
    "def_all_time",
    "never_midfield"
)

AMOUNT_OF_GAMES_TO_SIMULATE = 3

class Simulation :
    def __init__(self, player0 : dict = None, player1 : dict = None):
        self.player0 = player0
        self.player1 = player1
        self.data = []
        self.filepath = None

    def init_simulation_cfg(self,):
        if self.player0 is None:
            with open('player0.json', 'r') as json_file:
                self.player0 = json.load(json_file)

        if self.player1 is None:
            with open('player1.json', 'r') as json_file:
                self.player1 = json.load(json_file)

        self.data.append({
            "start_time" : time.strftime("%Y-%m-%d %H:%M:%S"),
            "table_config" : {
            "table_length": TABLE_LENGTH,
            "table_width": TABLE_WIDTH,
            "spring_length": SPRING_LENGTH,
            "pawn_size": PAWN_SIZE,
            "pawn_corner_radius": PAWN_CORNER_RADIUS,
            "pawn_separation": (SEP_DEF, SEP_MID, SEP_ATT),
            "blue_rod_positions": BLUE_ROD_POSITIONS,
            "red_rod_positions": RED_ROD_POSITIONS,
            "rod_thickness": ROD_THICKNESS,
            "net_thickness": NET_THICKNESS,
            "net_width": NET_WIDTH,
            "net_depth": NET_DEPTH,
            "ball_radius": BALL_RADIUS,
            "triangle_vert": TRIANGLE_VERT,
            "triangle_hori": TRIANGLE_HORI,
            "border_width": BORDER_WIDTH
            },
            "simulation_config" : {
            "dt": DT,
            "time_multiplier": TIME_MULTIPLIER,
            "ball_initial_position": BALL_INITIAL_POSITION,
            "ball_initial_velocity_magnitude": BALL_INITIAL_VELOCITY_MAGNITUDE,
            "ball_initial_velocity_angle": BALL_INITIAL_VELOCITY_ANGLE,
            "ball_max_velocity": BALL_MAX_VELOCITY,
            "ball_min_velocity": BALL_MIN_VELOCITY,
            "ball_friction_coefficient": BALL_FRICTION_COEFFICIENT
            },
            "player0" : {
                "reflexes" : self.player0["reflexes"],
                "transition_speed" : self.player0["transition_speed"],
                "strength" : self.player0["strength"],
                "technique" : self.player0["technique"],
                "strategy" : self.player0["strategy"]
            },
            "player1" : {
                "reflexes" : self.player1["reflexes"],
                "transition_speed" : self.player1["transition_speed"],
                "strength" : self.player1["strength"],
                "technique" : self.player1["technique"],
                "strategy" : self.player1["strategy"]
            }
        })

        # Define output file name
        filename = f"./simulation_results/{STRATEGY_ENUM[player0["strategy"]]}-{STRATEGY_ENUM[player1["strategy"]]}-{AMOUNT_OF_GAMES_TO_SIMULATE}-{self.data[0]['start_time'].replace(' ', '_')}.json"
        self.filepath = os.path.join(os.getcwd(), filename)

        with open(self.filepath, 'w') as json_file:
            json.dump(self.data, json_file, indent = 4)

    def set_custom_seed(self, seed : int):
        self.seed = seed
        babyfoot_table_vpython.set_seed(seed)

    def run_simulation(self, n_iterations : int):
        if self.filepath is None:
            raise ValueError("Simulation configuration not initialized. Call init_simulation_cfg() first.")
        
        for i in range(n_iterations):
            babyfoot_table_vpython.main(self.filepath)
    
    def get_results(self):
        if self.filepath is None:
            raise ValueError("Simulation configuration not initialized. Call init_simulation_cfg() first.")
        
        results = Results(self.filepath)
        results.load_results()
        results.parse_results()

        return results.data


class Results:
    def __init__(self, filepath : str):
        self.filepath = filepath
        self.games = None
        self.Ngames = None
        self.cfg = None
        self.data = {}

    def load_results(self):
        with open(self.filepath, 'r') as json_file:
            temp = json.load(json_file)
            self.cfg = temp[0]
            self.games = temp[1:]
            self.Ngames = len(self.games)

    def parse_results(self):
        for i in range(self.Ngames):
            game = self.games[i]
            player0_score = game["game_score"][0]
            player1_score = game["game_score"][1]
            simulation_duration = game["simulation_duration"]

            if "player0" not in self.data:
                self.data["player0"] = {
                    "score": [],
                    "win": 0,
                    "loss": 0,
                    "simulation_duration": []
                }
            if "player1" not in self.data:
                self.data["player1"] = {
                    "score": [],
                    "win": 0,
                    "loss": 0,
                    "simulation_duration": []
                }

            self.data["player0"]["score"].append(player0_score)
            self.data["player1"]["score"].append(player1_score)
            if player0_score > player1_score:
                self.data["player0"]["win"] += 1
                self.data["player1"]["loss"] += 1
            elif player0_score < player1_score:
                self.data["player0"]["loss"] += 1
                self.data["player1"]["win"] += 1
            self.data["player0"]["simulation_duration"].append(simulation_duration)
            self.data["player1"]["simulation_duration"].append(simulation_duration)


if __name__ == "__main__":
    player0 = {
        "reflexes": 10,
        "transition_speed": 10,
        "strength": 10,
        "technique": 10,
        "strategy": 0
    }
    player1 = {
        "reflexes": 10,
        "transition_speed": 10,
        "strength": 10,
        "technique": 10,
        "strategy": 0
    }
    simulation = Simulation(player0, player1)
    simulation.init_simulation_cfg()
    simulation.set_custom_seed(345)
    simulation.run_simulation(50)

    results = simulation.get_results()
    print("Simulation results:")
    print("Player 0:", results["player0"])
    print("Player 1:", results["player1"])

    print("Simulation completed.")