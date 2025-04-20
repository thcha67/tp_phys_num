from vpython import canvas, box, sphere, vector, color, rate, mag, text, arrow, label
import numpy as np
from player import Player
from utils import generate_rods, generate_pawns, generate_hand_identifiers, faceoff, is_ball_in_net, check_ball_pawn_collision, specular_reflection, controlled_shot, change_hand_identifier_color, update_score, generate_boxes

from config import *

import time
import json

def play_one_game(game_number):
    players : list[Player] = [Player(0), Player(1)]

    score = [0, 0]  #[blue team goals, red team goals]
    simulation_time = 0

    # Set up the scene
    scene = canvas(title='Babyfoot Table', width=800, height=600, userzoom=False)

    # Create the table
    table = box(pos=vector(0, 0, 0), size=vector(TABLE_LENGTH, TABLE_WIDTH, 0.1), color=color.green)
    score_box, score_label, time_box, time_label = generate_boxes(score, simulation_time, game_number)

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

    most_recent_pawn = None
    gameOver = False
    while not gameOver:
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
            transition_idx = 0
            for i, hand_iden in enumerate(hand_identifiers[player.team*4 : (player.team+1) * 4]):
                change_hand_identifier_color(transition_idx, i, player, hand_iden)

            closest_rod_to_ball = np.argmin(abs(player.rod_positions - ball.pos.x))

            new_velocity_magnitude = player.get_velocity()
            is_ball_controlled = player.is_ball_controlled()

            for pawn in player_pawns[closest_rod_to_ball]: # check for collisions with the closest rod to the ball
                if pawn == most_recent_pawn:
                    continue
                reflection_normal = check_ball_pawn_collision(ball, ball_velocity, pawn)

                if reflection_normal is not None: # collision detected
                    # ball cannot be controlled when coming from the back of the pawn
                    if ((player.team == 0 and ball_velocity.x > 0 and reflection_normal.x < 0) # blue team
                    or (player.team == 1 and ball_velocity.x < 0 and reflection_normal.x > 0)): # red team 
                        is_ball_controlled = False

                    # ball cannot be controlled if the player's hand is not on the rod
                    if closest_rod_to_ball not in player.hand_positions:
                        is_ball_controlled = False

                    if is_ball_controlled: # specular reflection
                        posts = blue_posts if player.team == 0 else red_posts
                        ball_velocity = controlled_shot(closest_rod_to_ball, ball, pawns, player, posts, new_velocity_magnitude, ball_velocity)
                    else:
                        ball_velocity = specular_reflection(ball_velocity, reflection_normal)
                        # if not hands
                    most_recent_pawn = pawn
                    break

        net_number = 0
        for net in [net_blue, net_red]:
            if is_ball_in_net(ball, net):
                if net_number == 0:
                    gameOver = update_score(1, score, score_label)
                else:
                    gameOver = update_score(0, score, score_label)
                faceoff(ball, ball_velocity)
            net_number += 1


    #save the game data to a json file
    new_data = {
        "game_number" : game_number,
        "game_score": score,
        "player_0" : {
        "reflexes": players[0].reflexes,
        "transition_speed": players[0].transition_time, 
        "strength": players[0].strength, 
        "technique": players[0].technique, 
        "strategy": players[0].strategy
        },
        "player_1" : {
        "reflexes": players[1].reflexes,
        "transition_speed": players[1].transition_time, 
        "strength": players[1].strength, 
        "technique": players[1].technique, 
        "strategy": players[1].strategy
        },
        "time" : time.strftime("%Y-%m-%d %H:%M:%S")
    }

    file_name = 'simulation_data.json'
    with open(file_name, 'r') as file:
        data = json.load(file)

    data.append(new_data)

    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

file_name = "simulation_data.json"
data = []
with open(file_name, 'w') as file:
    json.dump(data, file, indent=4)

for i in range(10):
    play_one_game(i)