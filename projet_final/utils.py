from config import *
from vpython import box, vector, color, label, sphere, mag, arrow
import numpy as np
from player import Player
import time

def update_score(teamNumber : int, score, score_label):
    score[teamNumber] = score[teamNumber] + 1
    score_label.text = f"{score[0]}    :   {score[1]}"

    if score[teamNumber] == 10:
        return True
    return False

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
    blue_pawns: list[box] = []
    red_pawns: list[box] = []

    # blue
    for i, rod_pos in enumerate(BLUE_ROD_POSITIONS):
        for pawn_pos in pawn_positions[i]:
            blue_pawns.append(box(pos=vector(rod_pos, pawn_pos, 0.15), size=vector(PAWN_SIZE[0], PAWN_SIZE[1], 1), color=color.blue))

    # red
    for i, rod_pos in enumerate(RED_ROD_POSITIONS):
        for pawn_pos in pawn_positions[i]:
            red_pawns.append(box(pos=vector(rod_pos, pawn_pos, 0.15), size=vector(PAWN_SIZE[0], PAWN_SIZE[1], 1), color=color.red))

    return  [
        [[blue_pawns[0]], [defender for defender in blue_pawns[1:3]], [mid for mid in blue_pawns[3:8]], [att for att in blue_pawns[8:11]]],
        [[red_pawns[0]], [defender for defender in red_pawns[1:3]], [mid for mid in red_pawns[3:8]], [att for att in red_pawns[8:11]]]
    ], blue_pawns + red_pawns

def faceoff(ball : sphere, ball_velocity : vector):
    ball.pos.x, ball.pos.y = np.random.uniform(-20, 20), np.random.uniform(-TABLE_WIDTH/3, TABLE_WIDTH/3)
    ball_velocity.x, ball_velocity.y = np.random.uniform(-20, 20), np.random.uniform(-20, 20)

    while ball_velocity.x == 0 or ball_velocity.y == 0:
        ball_velocity.x, ball_velocity.y = np.random.randint(-60, 60), np.random.randint(-20, 20)

    mag_factor = BALL_INITIAL_VELOCITY_MAGNITUDE/mag(ball_velocity)
    ball_velocity.x, ball_velocity.y = mag_factor*ball_velocity.x, mag_factor*ball_velocity.y
    return ball, ball_velocity

def is_ball_in_net(ball : sphere, net : box):
    if net.pos.x < 0:
        if -NET_WIDTH/2 < ball.pos.y < NET_WIDTH/2 and ball.pos.x < -TABLE_LENGTH/2 - BALL_RADIUS:
            return True
    else:
        if -NET_WIDTH/2 < ball.pos.y < NET_WIDTH/2 and ball.pos.x > TABLE_LENGTH/2 + BALL_RADIUS:
            return True
    return False


def check_ball_pawn_collision(ball, ball_velocity, pawn):
    # Relative position
    rel_x = ball.pos.x - pawn.pos.x
    rel_y = ball.pos.y - pawn.pos.y

    # Half sizes (inner rectangle area)
    inner_half_w = PAWN_SIZE[0] / 2 - PAWN_CORNER_RADIUS
    inner_half_h = PAWN_SIZE[1] / 2 - PAWN_CORNER_RADIUS

    # Clamp the ball's position to the nearest point on the pawn's rounded rectangle
    clamped_x = max(-inner_half_w, min(rel_x, inner_half_w))
    clamped_y = max(-inner_half_h, min(rel_y, inner_half_h))

    # Closest point on the rounded rectangle (including corners)
    closest_x = pawn.pos.x + clamped_x
    closest_y = pawn.pos.y + clamped_y

    # Compute vector from closest point to ball center
    diff_x = ball.pos.x - closest_x
    diff_y = ball.pos.y - closest_y
    dist_squared = diff_x**2 + diff_y**2
    collision_radius = ball.radius + PAWN_CORNER_RADIUS

    # Check actual distance to border
    if dist_squared <= collision_radius**2:
        normal = vector(diff_x, diff_y, 0).norm()
        return normal
    return None

def specular_reflection(ball_velocity, reflection_normal):
    # Calculate the dot product of the ball velocity and the reflection normal
    dot = ball_velocity.x * reflection_normal.x + ball_velocity.y * reflection_normal.y
    # Reflect the ball velocity using the reflection normal
    ball_velocity.x -= 2 * dot * reflection_normal.x
    ball_velocity.y -= 2 * dot * reflection_normal.y
    return ball_velocity*0.9 # 10% speed loss on collision

def controlled_shot(closest_rod_to_ball, ball, pawns, player, posts, new_velocity_magnitude, ball_velocity):
    opponent_pawns = pawns[1 - player.team]
    if closest_rod_to_ball == 3: # attackers rod, aim between the opponent's defenders and gk and towards the net (between the posts)
        pawns_to_avoid = posts + opponent_pawns[0] + opponent_pawns[1] # opponent's posts, goalkeeper and defenders
        extreme_vectors_x_position = pawns_to_avoid[0].pos.x # goal post position
        max_vector = vector(extreme_vectors_x_position, NET_WIDTH/2 - BALL_RADIUS, 0.15) - ball.pos
        min_vector = vector(extreme_vectors_x_position, -NET_WIDTH/2 + BALL_RADIUS, 0.15) - ball.pos

    else:
        if closest_rod_to_ball == 0: # goalkeeper rod, aim between the opponent's attackers and own defenders
            pawns_to_avoid = opponent_pawns[3] + pawns[player.team][1]
        elif closest_rod_to_ball == 1: # defenders rods, aim between the opponent's attackers
            pawns_to_avoid = opponent_pawns[3]
        else: # midfielders rod, aim between the opponent's midfielders
            pawns_to_avoid = opponent_pawns[2]

        extreme_vectors_x_position = pawns_to_avoid[0].pos.x
        max_vector = vector(extreme_vectors_x_position, TABLE_WIDTH/2 - BALL_RADIUS, 0.15) - ball.pos
        min_vector = vector(extreme_vectors_x_position, -TABLE_WIDTH/2 + BALL_RADIUS, 0.15) - ball.pos

    directions = []
    for alpha in np.linspace(0, 1, 20):
        vec = (1 - alpha) * min_vector + alpha * max_vector
        directions.append(vec.norm())

    best_direction = None
    best_min_dist = 0

    for direction in directions:
        min_dist = float('inf')
        for opponent in pawns_to_avoid:
            vec_to_opponent = opponent.pos - ball.pos
            # Distance from point to ray using 2D cross product
            dist_to_ray = abs(vec_to_opponent.x * direction.y - vec_to_opponent.y * direction.x)
            min_dist = min(min_dist, dist_to_ray)

        if min_dist > best_min_dist:
            best_min_dist = min_dist
            best_direction = direction

    # for direction in directions:
    #     arrow(pos=ball.pos, axis=direction*100, color=color.red, shaftwidth=0.5)
    # arrow(pos=ball.pos, axis=best_direction*200, color=color.green, shaftwidth=1)
    # time.sleep(1)
    # Apply redirection
    ball_velocity = best_direction * new_velocity_magnitude
    return ball_velocity

def change_hand_identifier_color(transition_idx : int, hand_idx : int, player : Player, hand_iden : box):
    if hand_idx in player.hand_positions:
        if player.transition_cooldown[transition_idx] == 0:
            hand_iden.color = player.color
        transition_idx += 1
    else:
        hand_iden.color = color.gray(0.5)

def pass_ball(pawn, rod_pawns, new_velocity_magnitude):
    # find the rod pawn that is the closest to the position y=0
    other_pawns = [rod_pawn for rod_pawn in rod_pawns if rod_pawn != pawn]
    closest_pawn = min(other_pawns, key=lambda x: abs(x.pos.y))

    direction = closest_pawn.pos - pawn.pos
    direction = direction.norm()

    # Apply redirection
    ball_velocity = direction * new_velocity_magnitude
    return ball_velocity