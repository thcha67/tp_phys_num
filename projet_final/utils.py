from config import *
from vpython import box, vector, color, label, sphere, mag
import numpy as np

def generate_rods():
    return [
    box(
        pos=vector(rod_position, 0, 0.15), 
        size=vector(ROD_THICKNESS, TABLE_WIDTH, 0.1), 
        color=color.gray(0.5)
    )
    for rod_position in BLUE_ROD_POSITIONS + RED_ROD_POSITIONS
]

def generate_hand_identifiers():
    hand_identifier_size = [20, 20] #[x_size, y_size]
    return [
    box(
        pos=vector(rod_position, -TABLE_WIDTH/2 - hand_identifier_size[1] - 20, 0.15), 
        size=vector(hand_identifier_size[0], hand_identifier_size[1], 0.1), 
        color=color.gray(0.5)
    )
    for rod_position in BLUE_ROD_POSITIONS + RED_ROD_POSITIONS
]

def generate_pawns():
    gk_pos = [0]
    def_pos = [-SEP_DEF/2, SEP_DEF/2]
    mid_pos = [-2*SEP_MID, -SEP_MID, 0, SEP_MID, 2*SEP_MID]
    att_pos = [-SEP_ATT, 0, SEP_ATT]

    pawn_positions = [gk_pos, def_pos, mid_pos, att_pos]

    # Create the players
    individual_pawns: list[box] = []

    # blue
    for i, rod_pos in enumerate(BLUE_ROD_POSITIONS):
        for pawn_pos in pawn_positions[i]:
            individual_pawns.append(box(pos=vector(rod_pos, pawn_pos, 0.15), size=vector(PAWN_SIZE[0], PAWN_SIZE[1], 1), color=color.blue))

    # red
    for i, rod_pos in enumerate(RED_ROD_POSITIONS):
        for pawn_pos in pawn_positions[i]:
            individual_pawns.append(box(pos=vector(rod_pos, pawn_pos, 0.15), size=vector(PAWN_SIZE[0], PAWN_SIZE[1], 1), color=color.red))

    return  [
        [[individual_pawns[0]], [defender for defender in individual_pawns[1:3]], [mid for mid in individual_pawns[3:8]], [att for att in individual_pawns[8:11]]],
        [[individual_pawns[11]], [defender for defender in individual_pawns[12:14]], [mid for mid in individual_pawns[14:19]], [att for att in individual_pawns[19:22]]]
    ], individual_pawns

def faceoff(ball : sphere, ball_velocity : vector):
    ball.pos.x, ball.pos.y = np.random.uniform(-20, 20), np.random.uniform(-TABLE_WIDTH/2, TABLE_WIDTH/2)
    ball_velocity.x, ball_velocity.y = np.random.uniform(-20, 20), np.random.uniform(-20, 20)

    while ball_velocity.x == 0 or ball_velocity.y == 0:
        ball_velocity.x, ball_velocity.y = np.random.randint(-60, 60), np.random.randint(-20, 20)

    mag_factor = BALL_INITIAL_VELOCITY_MAGNITUDE/mag(ball_velocity)
    ball_velocity.x, ball_velocity.y = mag_factor*ball_velocity.x, mag_factor*ball_velocity.y
    return ball, ball_velocity

