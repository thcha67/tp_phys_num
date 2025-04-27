import json
import os

DEFAULT_TABLE_CONFIG = {
    "table_length": 1140,
    "table_width": 700,
    "pawn_size": [11, 21, 1],
    "pawn_corner_radius": 3,
    "pawn_separation": [335, 122, 215],
    "blue_rod_positions": [-525, -375, -72, 228],
    "red_rod_positions": [525, 375, 72, -228],
    "rod_thickness": 5,
    "net_thickness": 0.1,
    "net_width": 204,
    "net_depth": 40,
    "ball_radius": 16,
    "triangle_vert" : 250,
    "triangle_hori" : 160,
    "border_width" : 40
}

DEFAULT_SIMULATION_CONFIG = {
    "dt": 0.02,
    "time_multiplier": 1,
    "ball_initial_position": [500, 0],
    "ball_initial_velocity_magnitude": 100,
    "ball_initial_velocity_angle": 0.1,
    "ball_max_velocity": 8000,
    "ball_min_velocity" : 50,
    "ball_friction_coefficient": 0.05
}

# Check if the configuration files exist, if not create them with default values
if os.path.exists("table_config.json"):
    with open("table_config.json", "r") as f:
        table_config = json.load(f)
        for key in DEFAULT_TABLE_CONFIG:
            if key not in table_config:
                table_config[key] = DEFAULT_TABLE_CONFIG[key]
else:
    with open("table_config.json", "w") as f:
        json.dump(DEFAULT_TABLE_CONFIG, f, indent=4)
    table_config = DEFAULT_TABLE_CONFIG

if os.path.exists("simulation_config.json"):
    with open("simulation_config.json", "r") as f:
        simulation_config = json.load(f)
        for key in DEFAULT_SIMULATION_CONFIG:
            if key not in simulation_config:
                simulation_config[key] = DEFAULT_SIMULATION_CONFIG[key]
else:
    with open("simulation_config.json", "w") as f:
        json.dump(DEFAULT_SIMULATION_CONFIG, f, indent=4)
    simulation_config = DEFAULT_SIMULATION_CONFIG


# Load the configuration values
TABLE_LENGTH = table_config["table_length"]
TABLE_WIDTH = table_config["table_width"]
SPRING_LENGTH = table_config["spring_length"]
PAWN_SIZE = table_config["pawn_size"]
PAWN_CORNER_RADIUS = table_config["pawn_corner_radius"]
SEP_DEF, SEP_MID, SEP_ATT = table_config["pawn_separation"]
BLUE_ROD_POSITIONS = table_config["blue_rod_positions"]
RED_ROD_POSITIONS = table_config["red_rod_positions"]
ROD_THICKNESS = table_config["rod_thickness"]
NET_THICKNESS = table_config["net_thickness"]
NET_WIDTH = table_config["net_width"]
NET_DEPTH = table_config["net_depth"]
BALL_RADIUS = table_config["ball_radius"]
TRIANGLE_VERT = table_config["triangle_vert"]
TRIANGLE_HORI = table_config["triangle_hori"]
BORDER_WIDTH = table_config["border_width"]

DT = simulation_config["dt"]
TIME_MULTIPLIER = simulation_config["time_multiplier"]
BALL_INITIAL_POSITION = simulation_config["ball_initial_position"]
BALL_INITIAL_VELOCITY_MAGNITUDE = simulation_config["ball_initial_velocity_magnitude"]
BALL_INITIAL_VELOCITY_ANGLE = simulation_config["ball_initial_velocity_angle"]
BALL_MAX_VELOCITY = simulation_config["ball_max_velocity"]
BALL_MIN_VELOCITY = simulation_config["ball_min_velocity"]
BALL_FRICTION_COEFFICIENT = simulation_config["ball_friction_coefficient"]


not_exportable = [
    "DEFAULT_TABLE_CONFIG",
    "DEFAULT_SIMULATION_CONFIG",
    "table_config",
    "simulation_config",
    "__name__",
]

# When using `from config import *`, we want to export all variables except the ones in `not_exportable`
__all__ = [
    config_option for config_option in dir() if config_option not in not_exportable
]