from vpython import canvas, box, sphere, vector, color, rate, mag, text, arrow, label
import numpy as np
from player import Player
from utils import generate_rods, generate_pawns, generate_hand_identifiers, faceoff

from config import *

import time

np.random.seed(1)

players = [Player(0), Player(1)]

score = [0, 0]  #[blue team goals, red team goals]
simulation_time = 0

# Set up the scene
scene = canvas(title='Babyfoot Table', width=800, height=600, userzoom=False)

# Create the table
table = box(pos=vector(0, 0, 0), size=vector(TABLE_LENGTH, TABLE_WIDTH, 0.1), color=color.green)
score_box = box(pos=vector(0, TABLE_WIDTH/2 + 100,10), size=vector(250,100,0), color=color.gray(0.5))
score_label = label(pos=score_box.pos, text=f"{score[0]}    :   {score[1]}", xoffset=0, yoffset=0, space=score_box.size.x, height=25, border=4, font='sans')
time_box = box(pos=vector(250, TABLE_WIDTH/2 + 100,10), size=vector(200,100,0), color=color.gray(0.5))
time_label = label(pos=time_box.pos, text=f"{simulation_time}s", xoffset=0, yoffset=0, space=score_box.size.x, height=25, border=4, font='sans')

rods = generate_rods()
pawns, individual_pawns = generate_pawns()
hand_identifiers = generate_hand_identifiers()

# Create the ball at the specified position
ball = sphere(pos=vector(BALL_INITIAL_POSITION[0], BALL_INITIAL_POSITION[1], 0.15), radius=BALL_RADIUS, color=color.white)
ball_velocity = vector(BALL_INITIAL_VELOCITY_MAGNITUDE*np.cos(BALL_INITIAL_VELOCITY_ANGLE), BALL_INITIAL_VELOCITY_MAGNITUDE*np.sin(BALL_INITIAL_VELOCITY_ANGLE), 0)
faceoff(ball, ball_velocity)

# Create the nets behind each goalkeeper
net_blue = box(pos=vector(-TABLE_LENGTH/2-NET_DEPTH/2, 0, 0.15), size=vector(NET_DEPTH, NET_WIDTH, NET_THICKNESS), color=color.white)
net_red = box(pos=vector(TABLE_LENGTH/2+NET_DEPTH/2, 0, 0.15), size=vector(NET_DEPTH, NET_WIDTH, NET_THICKNESS), color=color.white)


def update_score(teamNumber : int):
    score[teamNumber] = score[teamNumber] + 1
    score_label.text = f"{score[0]}    :   {score[1]}"


maximal_dist_of_collision = BALL_RADIUS + np.sqrt(PAWN_SIZE[0]**2 + PAWN_SIZE[1]**2) #maximal distance between the ball and the player to be considered as a collision


most_recent_pawn = None
while True:
    rate(TIME_MULTIPLIER/DT) # control the simulation speed
    simulation_time += DT
    time_label.text = f"{round(simulation_time, 4)}s"
    # Move the ball
    ball.pos += ball_velocity * DT
    
    #check if players changes hand position, and move the rods
    for player in players:
        player_pawns = pawns[player.team]
        player.move_hands(ball)

        #calculate the displacement of each rod
        for i, rod_number in enumerate(player.hand_positions):
            displacement = player.calculate_rod_displacement(ball, ball_velocity, player_pawns, rod_number, i)
            player.move_rod(rod_number, displacement, player_pawns)

        #change the color of the hand identifiers
        team_color = color.blue
        if player.team == 1:
            team_color = color.red
        hand_idx = 0
        for i, hand_iden in enumerate(hand_identifiers[player.team*4 : (player.team+1) * 4]):
            if i in player.hand_positions:
                if player.transition_cooldown[hand_idx] == 0:
                    hand_iden.color= team_color
                hand_idx += 1
            else:
                hand_iden.color = color.gray(0.5)

    # apply friction, 0 = no friction
    ball_velocity.x = (1 - BALL_FRICTION_COEFFICIENT*DT) * ball_velocity.x
    ball_velocity.y = (1 - BALL_FRICTION_COEFFICIENT*DT) * ball_velocity.y

    # Check for collisions with table boundaries
    if abs(ball.pos.x) >= TABLE_LENGTH/2 - BALL_RADIUS:
        ball_velocity.x *= -1
        most_recent_pawn = None

    if abs(ball.pos.y) >= TABLE_WIDTH/2 - BALL_RADIUS:
        ball_velocity.y *= -1
        most_recent_pawn = None

    # Check for collisions with players
    for pawn in individual_pawns:
        pawn_to_ball = ball.pos - pawn.pos

        if mag(pawn_to_ball) <= maximal_dist_of_collision and most_recent_pawn != pawn:
            dx = abs(pawn_to_ball.x)
            dy = abs(pawn_to_ball.y)

            inner_half_w = PAWN_SIZE[0] / 2 - PAWN_CORNER_RADIUS
            inner_half_h = PAWN_SIZE[1] / 2 - PAWN_CORNER_RADIUS
            outer_half_w = inner_half_w + PAWN_CORNER_RADIUS
            outer_half_h = inner_half_h + PAWN_CORNER_RADIUS

            # Check side collisions
            if dx <= inner_half_w and dy <= outer_half_h:
                ball_velocity.x *= -1
                most_recent_pawn = pawn
                break
            elif dy <= inner_half_h and dx <= outer_half_w:
                ball_velocity.y *= -1
                most_recent_pawn = pawn
                break

            # Check corner collisions
            corner_centers = [
                vector(pawn.pos.x - inner_half_w, pawn.pos.y - inner_half_h, 0.15),  # bottom left
                vector(pawn.pos.x + inner_half_w, pawn.pos.y - inner_half_h, 0.15),  # bottom right
                vector(pawn.pos.x - inner_half_w, pawn.pos.y + inner_half_h, 0.15),  # top left
                vector(pawn.pos.x + inner_half_w, pawn.pos.y + inner_half_h, 0.15),  # top right
            ]

            for corner in corner_centers:
                diff = ball.pos - corner
                dist_squared = diff.x**2 + diff.y**2
                collision_radius = ball.radius + PAWN_CORNER_RADIUS

                if dist_squared <= collision_radius**2:
                    normal = diff.norm()  # unit vector from corner to ball center
                    dot = ball_velocity.x * normal.x + ball_velocity.y * normal.y
                    ball_velocity.x -= 2 * dot * normal.x
                    ball_velocity.y -= 2 * dot * normal.y
                    most_recent_pawn = pawn
                    break
    
    net_number = 0
    for net in [net_blue, net_red]:
        if abs(ball.pos.x - net.pos.x) < (ball.radius + net.size.x / 2) and abs(ball.pos.y - net.pos.y) < (ball.radius + net.size.y / 2):
            if net_number == 0:
                update_score(1)
                time.sleep(0.5)
                faceoff(ball, ball_velocity)
                time.sleep(0.5)
            else:
                update_score(0)
                time.sleep(0.5)
                faceoff(ball, ball_velocity)
                time.sleep(0.5)
        net_number += 1