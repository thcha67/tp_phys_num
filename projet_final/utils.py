from config import *
from vpython import box, vector, color, label
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


tr_corner_angles = [0.983, 1.337]
tl_corner_angles = [np.pi-1.337, np.pi-0.983]
br_corner_angles = [-0.983, -1.337]
bl_corner_angles = [1.337-np.pi, 0.983-np.pi]