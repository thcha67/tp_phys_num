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
    def __init__(self, player0, player1):
        self.player0 = player0
        self.player1 = player1
        self.data = []
        self.filepath = None

    def init_simulation_cfg(self,):
        with open('player0.json', 'r') as json_file:
            player0 = json.load(json_file)

        with open('player1.json', 'r') as json_file:
            player1 = json.load(json_file)

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
                "reflexes" : player0["reflexes"],
                "transition_speed" : player0["transition_speed"],
                "strength" : player0["strength"],
                "technique" : player0["technique"],
                "strategy" : player0["strategy"]
            },
            "player1" : {
                "reflexes" : player1["reflexes"],
                "transition_speed" : player1["transition_speed"],
                "strength" : player1["strength"],
                "technique" : player1["technique"],
                "strategy" : player1["strategy"]
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


if __name__ == "__main__":
    player0 = "player0.json"
    player1 = "player1.json"
    simulation = Simulation(player0, player1)
    simulation.init_simulation_cfg()
    simulation.set_custom_seed(42)
    simulation.run_simulation(AMOUNT_OF_GAMES_TO_SIMULATE)