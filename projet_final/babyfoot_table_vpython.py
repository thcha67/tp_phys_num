from vpython import canvas, box, sphere, vector, color, rate, mag, text, arrow, label
import numpy as np
from player import Player
from utils import generate_rods, generate_pawns

from config import *


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

# Create the ball at the specified position
ball = sphere(pos=vector(BALL_INITIAL_POSITION[0], BALL_INITIAL_POSITION[1], 0.15), radius=BALL_RADIUS, color=color.white)
ball_velocity = vector(BALL_INITIAL_VELOCITY_MAGNITUDE*np.cos(BALL_INITIAL_VELOCITY_ANGLE), BALL_INITIAL_VELOCITY_MAGNITUDE*np.sin(BALL_INITIAL_VELOCITY_ANGLE), 0)

# Create the nets behind each goalkeeper
net_blue = box(pos=vector(-TABLE_LENGTH/2-NET_DEPTH/2, 0, 0.15), size=vector(NET_DEPTH, NET_WIDTH, NET_THICKNESS), color=color.white)
net_red = box(pos=vector(TABLE_LENGTH/2+NET_DEPTH/2, 0, 0.15), size=vector(NET_DEPTH, NET_WIDTH, NET_THICKNESS), color=color.white)


def update_score(teamNumber : int):
    score[teamNumber] = score[teamNumber] + 1
    score_label.text = f"{score[0]}    :   {score[1]}"


maximal_dist_of_collision = BALL_RADIUS + np.sqrt(PAWN_SIZE[0]**2 + PAWN_SIZE[1]**2) #maximal distance between the ball and the player to be considered as a collision


most_recent_pawn = None
recent_goal = False
while True:
    rate(TIME_MULTIPLIER/DT) # control the simulation speed
    simulation_time += DT
    time_label.text = f"{round(simulation_time, 4)}s"
    # Move the ball
    ball.pos += ball_velocity * DT
    
    #check if players changes hand position, and move the rods TODO: put transition time
    for player in players:
        player_pawns = pawns[player.team]
        player.move_hands(ball)

        for i, rod_number in enumerate(player.hand_positions):
            displacement = player.calculate_rod_displacement(ball, ball_velocity, player_pawns, rod_number, i)
            player.move_rod(rod_number, displacement, player_pawns)

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

        # check if the ball is close enough that it could touch in the right angle and if the pawn is not the most recent pawn to touch the ball
        if mag(pawn_to_ball) <= maximal_dist_of_collision and most_recent_pawn != pawn:
            if abs(pawn_to_ball.x) > 5.5 and abs(pawn_to_ball.y) < 10.5: # the ball is reflected on the vertical sides
                ball_velocity.x *= -1
                most_recent_pawn = pawn
                break

            elif abs(pawn_to_ball.y) > 10.5 and abs(pawn_to_ball.x) < 5.5: # the ball is reflected on the horizontal sides
                ball_velocity.y *= -1
                most_recent_pawn = pawn
                break

    net_number = 0
    for net in [net_blue, net_red]:
        if not recent_goal:
            if abs(ball.pos.x - net.pos.x) < (ball.radius + net.size.x / 2) and abs(ball.pos.y - net.pos.y) < (ball.radius + net.size.y / 2):
                if net_number == 0:
                    update_score(1)
                    recent_goal = True
                else:
                    update_score(0)
                    recent_goal = True
        net_number += 1