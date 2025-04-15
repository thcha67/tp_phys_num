from vpython import canvas, box, sphere, vector, color, rate, mag, text, arrow, label
import numpy as np
from player import Player
import time

from config import *

gk_pos = [0]
def_pos = [-SEP_DEF/2, SEP_DEF/2]
mid_pos = [-2*SEP_MID, -SEP_MID, 0, SEP_MID, 2*SEP_MID]
att_pos = [-SEP_ATT, 0, SEP_ATT]

pawn_positions = [gk_pos, def_pos, mid_pos, att_pos]

player_blue = Player(
    team=0, 
    reflexes=8, 
    transition_speed=5, 
    strength=5, 
    technique=5, 
    strategy=0
)

player_red = Player(
    team=1, 
    reflexes=3,
    transition_speed=5, 
    strength=5, 
    technique=5, 
    strategy=1
)

players = [player_blue, player_red]

score = [0, 0]  #[blue team goals, red team goals]

# Set up the scene
scene = canvas(title='Babyfoot Table', width=800, height=600, userzoom=False)

# Create the table
table = box(pos=vector(0, 0, 0), size=vector(TABLE_LENGTH, TABLE_WIDTH, 0.1), color=color.green)
score_position = vector(0, TABLE_WIDTH/2 + 100,10)
score_box = box(pos=score_position, size=vector(500,100,0), color=color.gray(0.5))
score_label = label(pos=score_box.pos, text=f"{score[0]}    :   {score[1]}", xoffset=0, yoffset=0, space=score_box.size.x, height=25, border=4, font='sans')

# Create the rods
rods = [
    box(pos=vector(rod_position, 0, 0.15), size=vector(ROD_THICKNESS, TABLE_WIDTH, 0.1), color=color.gray(0.5))
    for rod_position in BLUE_ROD_POSITIONS + RED_ROD_POSITIONS
]

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


# Create the ball at the specified position
ball = sphere(pos=vector(BALL_INITIAL_POSITION[0], BALL_INITIAL_POSITION[1], 0.15), radius=BALL_RADIUS, color=color.white)
ball_velocity = vector(BALL_INITIAL_VELOCITY_MAGNITUDE*np.cos(BALL_INITIAL_VELOCITY_ANGLE), BALL_INITIAL_VELOCITY_MAGNITUDE*np.sin(BALL_INITIAL_VELOCITY_ANGLE), 0)

# Create the nets behind each goalkeeper
net_blue = box(pos=vector(-TABLE_LENGTH/2-NET_DEPTH/2, 0, 0.15), size=vector(NET_DEPTH, NET_WIDTH, NET_THICKNESS), color=color.white)
net_red = box(pos=vector(TABLE_LENGTH/2+NET_DEPTH/2, 0, 0.15), size=vector(NET_DEPTH, NET_WIDTH, NET_THICKNESS), color=color.white)


pawns = [
    [[individual_pawns[0]], [defender for defender in individual_pawns[1:3]], [mid for mid in individual_pawns[3:8]], [att for att in individual_pawns[8:11]]],
    [[individual_pawns[11]], [defender for defender in individual_pawns[12:14]], [mid for mid in individual_pawns[14:19]], [att for att in individual_pawns[19:22]]]
]

# blue_pawns = [[individual_pawns[0]], [defender for defender in individual_pawns[1:3]], [mid for mid in individual_pawns[3:8]], [att for att in individual_pawns[8:11]]]
# red_pawns = [[individual_pawns[11]], [defender for defender in individual_pawns[12:14]], [mid for mid in individual_pawns[14:19]], [att for att in individual_pawns[19:22]]]

def update_score(teamNumber : int):
    score[teamNumber] = score[teamNumber] + 1
    score_label.text = f"{score[0]}    :   {score[1]}"

# corner angles
maximal_dist_of_collision = BALL_RADIUS + np.sqrt(PAWN_SIZE[0]**2 + PAWN_SIZE[1]**2) #maximal distance between the ball and the player to be considered as a collision
corner_angles = [0.983, 1.337, np.pi-1.337, np.pi-0.983] # in radians

most_recent_pawn = None
recent_goal = False
while True:
    rate(400)
    # Move the ball
    ball.pos += ball_velocity * DT
    
    #check if players changes hand position, and move the rods TODO: put transition time
    for player in players:
        player_pawns = pawns[player.team]
        player.move_hands(ball)

        for i, rod_number in enumerate(player.hand_positions):
            displacement = player.calculate_rod_displacement(ball, ball_velocity, player_pawns, rod_number)
            player.move_rod(rod_number, displacement, player_pawns)

    # apply friction, 0 = no friction
    ball_velocity.x = (1 - BALL_FRICTION_COEFFICIENT*DT) * ball_velocity.x
    ball_velocity.y = (1 - BALL_FRICTION_COEFFICIENT*DT) * ball_velocity.y

    # Check for collisions with table boundaries
    if abs(ball.pos.x) > TABLE_LENGTH/2 - BALL_RADIUS:
        ball_velocity.x *= -1
        most_recent_pawn = None
    if abs(ball.pos.y) > TABLE_WIDTH/2 - BALL_RADIUS:
        ball_velocity.y *= -1
        most_recent_pawn = None

    # Check for collisions with players
    for pawn in individual_pawns:
        pawn_to_ball_vct = pawn.pos - ball.pos
        pawn_to_ball_distance = mag(pawn_to_ball_vct)

        # check if the ball is close enough that it could touch in the right angle and if the pawn is not the most recent pawn to touch the ball
        if pawn_to_ball_distance < maximal_dist_of_collision and most_recent_pawn != pawn: 
            # check what part of the pawn is touching the ball (the corners or the sides)
            if abs(ball.pos.x - pawn.pos.x) < (ball.radius + pawn.size.x / 2) and abs(ball.pos.y - pawn.pos.y) < (ball.radius + pawn.size.y / 2):
                recent_goal = False

                x_pos, y_pos = -pawn_to_ball_vct.x, -pawn_to_ball_vct.y
                center_to_center_angle = np.arctan2(y_pos, x_pos)
                
                if ((corner_angles[0] < abs(center_to_center_angle) < corner_angles[1]) or
                    (corner_angles[2] < abs(center_to_center_angle) < corner_angles[3])):

                    incoming_velocity = mag(ball_velocity)
                    incoming_angle = np.arctan2(ball_velocity.y, ball_velocity.x)

                    # calculate the angle between the center of the circlar corners of the pawn and the center of the ball
                    center_of_circular_corner = pawn.pos + vector(2.5, 8.5, 0)
                    normal_angle = np.arctan2(ball.pos.y - center_of_circular_corner.y, ball.pos.x - center_of_circular_corner.x)

                    outcoming_angle = 2*normal_angle - incoming_angle - np.pi

                    ball_velocity.x = incoming_velocity*np.cos(outcoming_angle)
                    ball_velocity.y = incoming_velocity*np.sin(outcoming_angle)


                elif corner_angles[1] < abs(center_to_center_angle) < corner_angles[2]:
                    ball_velocity.y *= -1
                else:
                    ball_velocity.x *= -1
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