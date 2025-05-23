from config import *
from vpython import box, vector, color, label, sphere, mag, arrow, triangle, quad, vertex
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
        pos=vector(rod_position, 0, 0.25), 
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

def generate_triangles():

    tri_height = 0.15
    
    pos_vec_1 = vector(-TABLE_LENGTH/2, -TABLE_WIDTH/2, 0)
    v0, v1, v2 = vertex(pos=vector(0, 0, tri_height) + pos_vec_1), vertex(pos=vector(TRIANGLE_HORI, 0, tri_height) + pos_vec_1), vertex(pos=vector(0, TRIANGLE_VERT, tri_height) + pos_vec_1)
    tri_1 = triangle(v0=v0, v1=v1, v2=v2)

    pos_vec_2 = vector(TABLE_LENGTH/2, -TABLE_WIDTH/2, 0)
    v0, v1, v2 = vertex(pos=vector(0, 0, tri_height) + pos_vec_2), vertex(pos=vector(-TRIANGLE_HORI, 0, tri_height) + pos_vec_2), vertex(pos=vector(0, TRIANGLE_VERT, tri_height) + pos_vec_2)
    tri_2 = triangle(v0=v0, v1=v1, v2=v2)

    pos_vec_3 = vector(TABLE_LENGTH/2, TABLE_WIDTH/2, 0)
    v0, v1, v2 = vertex(pos=vector(0, 0, tri_height) + pos_vec_3), vertex(pos=vector(-TRIANGLE_HORI, 0, tri_height) + pos_vec_3), vertex(pos=vector(0, -TRIANGLE_VERT, tri_height) + pos_vec_3)
    tri_3 = triangle(v0=v0, v1=v1, v2=v2)

    pos_vec_4 = vector(-TABLE_LENGTH/2, TABLE_WIDTH/2, 0)
    v0, v1, v2 = vertex(pos=vector(0, 0, tri_height) + pos_vec_4), vertex(pos=vector(TRIANGLE_HORI, 0, tri_height) + pos_vec_4), vertex(pos=vector(0, -TRIANGLE_VERT, tri_height) + pos_vec_4)
    tri_4 = triangle(v0=v0, v1=v1, v2=v2)

    return [tri_1, tri_2, tri_3, tri_4]

def generate_borders():
    border_height = 0.15
    upper_border = box(pos=vector(0, TABLE_WIDTH/2 - BORDER_WIDTH/2, border_height), size=vector(TABLE_LENGTH - 2*TRIANGLE_HORI + 50, BORDER_WIDTH, border_height), color=color.gray(1))
    lower_border = box(pos=vector(0, -TABLE_WIDTH/2 + BORDER_WIDTH/2, border_height), size=vector(TABLE_LENGTH - 2*TRIANGLE_HORI + 50, BORDER_WIDTH, border_height), color=color.gray(1))

    return [upper_border, lower_border]

def faceoff(ball : sphere):
    #ball.pos.x, ball.pos.y = -450, 0
    #ball_velocity = vector(-40,0,0)
    ball.pos.x, ball.pos.y = np.random.uniform(-20, 20), np.random.uniform(-TABLE_WIDTH/3, TABLE_WIDTH/3)
    ball_velocity = vector(np.random.uniform(-20, 20), np.random.uniform(-20, 20), 0)

    ball_velocity.x, ball_velocity.y = BALL_INITIAL_VELOCITY_MAGNITUDE*ball_velocity.x, BALL_INITIAL_VELOCITY_MAGNITUDE*ball_velocity.y
    return ball, ball_velocity

def is_ball_in_net(ball : sphere, net : box):
    if net.pos.x < 0:
        if -NET_WIDTH/2 < ball.pos.y < NET_WIDTH/2 and ball.pos.x < -TABLE_LENGTH/2 - BALL_RADIUS:
            return True
    else:
        if -NET_WIDTH/2 < ball.pos.y < NET_WIDTH/2 and ball.pos.x > TABLE_LENGTH/2 + BALL_RADIUS:
            return True
    return False

def inelastic_collision(ball_velocity : vector , collision_object : str):
    if collision_object == "table_boundary_x":
        velocity_factor = min(np.random.normal(0.7, 0.2), 0.9)
    elif collision_object == "table_boundary_y":
        velocity_factor  = min(np.random.normal(0.8, 0.1), 0.9)
    else: #collision with pawns
        velocity_factor  = min(np.random.normal(0.7, 0.15), 0.9)
    ball_velocity *= velocity_factor
    return ball_velocity

def check_ball_pawn_collision(ball, pawn):
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
    return inelastic_collision(ball_velocity, "pawn_specular")

def diffuse_reflection(ball_velocity):
    new_angle = np.random.uniform(0, 2 * np.pi) # random angle between 0 and 2pi
    new_velocity = vector(np.cos(new_angle), np.sin(new_angle), 0) * mag(ball_velocity) # keep the same speed
    return inelastic_collision(new_velocity, "pawn_diffuse")

def controlled_shot(closest_rod_to_ball, ball, pawns, player, posts, new_velocity_magnitude, ball_velocity):
    opponent_pawns = pawns[1 - player.team]
    if closest_rod_to_ball == 3: # attackers rod, aim between the opponent's defenders and gk and towards the net (between the posts)
        pawns_to_avoid = posts + opponent_pawns[0] + opponent_pawns[1] # opponent's posts, goalkeeper and defenders
        extreme_vectors_x_position = posts[0].pos.x#pawns_to_avoid[0].pos.x # goal post position
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

    # center a distribution on the best direction, the std dev depends on the player's technique
    #min_angle = np.arctan2(min_vector.y, min_vector.x)
    #max_angle = np.arctan2(max_vector.y, max_vector.x)
    half_angle_range = min_vector.diff_angle(max_vector) / 2
    best_angle = np.arctan2(best_direction.y, best_direction.x)

    # new angle std from 0.1 (technique 10) to 1 (technique 0)
    new_angle_std_dev = (-0.09*player.technique + 1) * half_angle_range
    new_angle = np.random.normal(best_angle, new_angle_std_dev)

    new_direction = vector(np.cos(new_angle), np.sin(new_angle), 0)

    # for direction in directions:
    #     arrow(pos=ball.pos, axis=direction*100, color=color.red, shaftwidth=0.5)
    # arrow(pos=ball.pos, axis=best_direction*200, color=color.blue, shaftwidth=1)
    # arrow(pos=ball.pos, axis=new_direction*200, color=color.purple, shaftwidth=1)
    # time.sleep(2)
    # Apply redirection
    ball_velocity = new_direction * new_velocity_magnitude
    return ball_velocity

def pass_ball(pawn, rod_pawns, new_velocity_magnitude):
    # find the rod pawn that is the closest to the position y=0
    other_pawns = [rod_pawn for rod_pawn in rod_pawns if rod_pawn != pawn]
    closest_pawn = min(other_pawns, key=lambda x: abs(x.pos.y))

    direction = closest_pawn.pos - pawn.pos
    direction = direction.norm()
    
    # Apply redirection
    ball_velocity = direction * new_velocity_magnitude / 10 # 10% of the velocity for passess
    return ball_velocity


def check_if_ball_is_on_triangle(ball : sphere, triangle : triangle):
    m = TRIANGLE_VERT/TRIANGLE_HORI
    b = -990.625 #hard coded ark degeu
    if ball.pos.y < abs(m*ball.pos.x) + b or ball.pos.y > -abs(m*ball.pos.x) - b:
        return True
    
def modify_velocity_on_triangle(ball : sphere, ball_velocity : vector):
    triangle_accel_x, triangle_accel_y = 113.6, 72.8            
    if ball.pos.x > 0 and ball.pos.y > 0: #upper right
        ball_velocity.x += -triangle_accel_x / DT**-1
        ball_velocity.y += -triangle_accel_y / DT**-1
    elif ball.pos.x > 0 and ball.pos.y < 0: #lower right
        ball_velocity.x += -triangle_accel_x / DT**-1
        ball_velocity.y += triangle_accel_y/ DT**-1
    elif ball.pos.x < 0 and ball.pos.y < 0: #lower left
        ball_velocity.x += triangle_accel_x / DT**-1
        ball_velocity.y += triangle_accel_y / DT**-1
    elif ball.pos.x < 0 and ball.pos.y > 0: #upper left
        ball_velocity.x += triangle_accel_x / DT**-1
        ball_velocity.y += -triangle_accel_y / DT**-1

def check_if_ball_is_on_border(ball : sphere, border : box):
    if abs(ball.pos.y ) + BALL_RADIUS > abs(border.pos.y) - BORDER_WIDTH/2:
        return True
    
def modify_velocity_on_border(ball : sphere, ball_velocity : vector):
    accel_y = 72.8
    if ball.pos.y > 0:
        ball_velocity.y += -accel_y / DT**-1
    else:
        ball_velocity.y += accel_y / DT**-1

def is_hand_available(hand_number, transition_cooldowns):
    if transition_cooldowns[hand_number] <= 0:
        return True
    else:
        return False
    
def change_hand_identifier_color(hand_idx : int, player : Player, hand_iden : box):
    if hand_idx in player.hand_positions:
        if is_hand_available(hand_idx, player.transition_cooldown):
            hand_iden.color = player.color
    else:
        hand_iden.color = color.gray(0.5)

def apply_air_friction(ball_velocity : vector):
    """Apply air friction to the ball velocity."""
    speed = mag(ball_velocity)
    accel = -3*speed**2 / (16*BALL_RADIUS)
    new_speed = speed + accel*DT
    return ball_velocity * (new_speed/speed) if new_speed > 0 else 0
