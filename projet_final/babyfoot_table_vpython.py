from vpython import canvas, box, sphere, vector, color, rate, mag, text, arrow, label
import numpy as np
from player import Player
from utils import generate_rods, generate_pawns, generate_hand_identifiers, faceoff, is_ball_in_net, check_ball_pawn_collision, specular_reflection, controlled_shot, pass_ball

from config import *

import time

np.random.seed(2)

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

blue_posts = [
    sphere(pos=vector(TABLE_LENGTH/2, -NET_WIDTH/2, 0.15), visible=False),
    sphere(pos=vector(TABLE_LENGTH/2, NET_WIDTH/2, 0.15), visible=False)
]
red_posts = [
    sphere(pos=vector(-TABLE_LENGTH/2, -NET_WIDTH/2, 0.15), visible=False),
    sphere(pos=vector(-TABLE_LENGTH/2, NET_WIDTH/2, 0.15), visible=False)
]



def update_score(teamNumber : int):
    score[teamNumber] = score[teamNumber] + 1
    score_label.text = f"{score[0]}    :   {score[1]}"


maximal_dist_of_collision = BALL_RADIUS + np.sqrt(PAWN_SIZE[0]**2 + PAWN_SIZE[1]**2) #maximal distance between the ball and the player to be considered as a collision


a = []

most_recent_pawn = None
while True:
    rate(TIME_MULTIPLIER/DT) # control the simulation speed
    simulation_time += DT
    time_label.text = f"{round(simulation_time, 4)}s"
    # Move the ball
    ball.pos += ball_velocity * DT

    # apply friction, 0 = no friction
    ball_velocity.x = (1 - BALL_FRICTION_COEFFICIENT*DT) * ball_velocity.x
    ball_velocity.y = (1 - BALL_FRICTION_COEFFICIENT*DT) * ball_velocity.y

    # Check for collisions with table boundaries
    if abs(ball.pos.x) >= TABLE_LENGTH/2 - BALL_RADIUS:
        if -NET_WIDTH/2 + BALL_RADIUS < ball.pos.y < NET_WIDTH/2 - BALL_RADIUS: #its going into the net
            pass
        else:
            ball_velocity.x *= -1
            most_recent_pawn = None

    if abs(ball.pos.y) >= TABLE_WIDTH/2 - BALL_RADIUS:
        ball_velocity.y *= -1
        most_recent_pawn = None
    
    #check if players changes hand position, and move the rods. Also check for collisions with the pawns
    for player in players:
        player_pawns = pawns[player.team]
        player.move_hands(ball)

        #calculate the displacement of each rod
        for i, rod_index in enumerate(player.hand_positions):
            displacement = player.calculate_rod_displacement(ball, ball_velocity, player_pawns, rod_index, i)
            player.move_rod(rod_index, displacement, player_pawns)

        #change the color of the hand identifiers
        hand_idx = 0
        for i, hand_iden in enumerate(hand_identifiers[player.team*4 : (player.team+1) * 4]):
            if i in player.hand_positions:
                if player.transition_cooldown[hand_idx] == 0:
                    hand_iden.color = player.color
                hand_idx += 1
            else:
                hand_iden.color = color.gray(0.5)

        closest_rod_to_ball = np.argmin(abs(player.rod_positions - ball.pos.x))

        new_velocity_magnitude = player.get_velocity()
        
        is_ball_controlled = player.is_ball_controlled(mag(ball_velocity))
        can_pass = player.can_pass(mag(ball_velocity))

        rod_pawns = player_pawns[closest_rod_to_ball]

        for pawn in rod_pawns: # check for collisions with the closest rod to the ball
            if pawn == most_recent_pawn:
                continue
            reflection_normal = check_ball_pawn_collision(ball, ball_velocity, pawn)

            if reflection_normal is not None: # collision detected

                # ball cannot be controlled if the player's hand is not on the rod
                if closest_rod_to_ball not in player.hand_positions:
                    is_ball_controlled = False

                relative_incoming_angle = reflection_normal.diff_angle(vector(1 - 2*player.team, 0, 0)) # pi: from the back, pi/2 on top or bottom, 0 from the front

                if relative_incoming_angle > np.pi/2: # ball is coming from the back of the pawn (back side or back corners)
                    is_ball_controlled *= np.random.rand() < 0.25 # divide the probability of controlling the ball by 4

                elif relative_incoming_angle != 0: # ball is coming from top/bottom or front corners
                    is_ball_controlled *= np.random.rand() < 0.5 # divide the probability of controlling the ball by 2
                
                if is_ball_controlled: # specular reflection
                    if can_pass and closest_rod_to_ball != 0: # goalkeeper cannot pass
                        print("pass")
                        ball_velocity = pass_ball(pawn, rod_pawns, new_velocity_magnitude)
                    else:
                        print("shot")
                        posts = blue_posts if player.team == 0 else red_posts
                        ball_velocity = controlled_shot(closest_rod_to_ball, ball, pawns, player, posts, new_velocity_magnitude, ball_velocity)
                else:
                    print("not controlled")
                    ball_velocity = specular_reflection(ball_velocity, reflection_normal)
                        # if not hands
                most_recent_pawn = pawn
                break

    net_number = 0
    for net in [net_blue, net_red]:
        if is_ball_in_net(ball, net):
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


print(np.mean(a))