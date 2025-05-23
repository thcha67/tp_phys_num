from vpython import canvas, box, sphere, vector, color, rate, mag, text, arrow, label
import numpy as np
from player import Player
from utils import *
from config import *

import time
import json

def main(outputfile : str):
    players : list[Player] = [Player(0), Player(1)]

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
    triangles, borders = generate_triangles(), generate_borders()

    # Create the ball at the specified position
    ball = sphere(pos=vector(BALL_INITIAL_POSITION[0], BALL_INITIAL_POSITION[1], 0.15), radius=BALL_RADIUS, color=color.white)
    ball_velocity = vector(0, 0, 0)
    ball, ball_velocity = faceoff(ball)

    # Create the nets behind each goalkeeper
    net_blue = box(pos=vector(-TABLE_LENGTH/2-NET_DEPTH/2, 0, 0.15), size=vector(NET_DEPTH, NET_WIDTH, NET_THICKNESS), color=color.white)
    net_red = box(pos=vector(TABLE_LENGTH/2+NET_DEPTH/2, 0, 0.15), size=vector(NET_DEPTH, NET_WIDTH, NET_THICKNESS), color=color.white)

    red_posts = [
        sphere(pos=vector(TABLE_LENGTH/2, -NET_WIDTH/2, 0.15), visible=False, color=color.red, radius=20),
        sphere(pos=vector(TABLE_LENGTH/2, NET_WIDTH/2, 0.15), visible=False, color=color.red, radius=20)
    ]
    blue_posts = [
        sphere(pos=vector(-TABLE_LENGTH/2, -NET_WIDTH/2, 1), visible=False, color=color.blue, radius=20),
        sphere(pos=vector(-TABLE_LENGTH/2, NET_WIDTH/2, 1), visible=False, color=color.blue, radius=20)
    ]

    most_recent_pawn = None
    displacement_error = np.random.normal(0, 5)
    gameOver = False

    time_since_last_collision = 0
    

    while not gameOver:
        rate(TIME_MULTIPLIER/DT) # control the simulation speed
        simulation_time += DT
        time_label.text = f"{simulation_time:.2f}s"

        time_since_last_collision += DT

        if time_since_last_collision > 5: # faceofff if no collision for 5s
            ball, ball_velocity = faceoff(ball)
            time_since_last_collision = 0

        # Move the ball
        ball.pos += ball_velocity * DT

        # apply friction, 0 = no friction
        apply_air_friction(ball_velocity)
        # if mag(ball_velocity) < BALL_MIN_VELOCITY:
        #     ball, ball_velocity = faceoff(ball)

        # Check for collisions with table boundaries
        if abs(ball.pos.x) >= TABLE_LENGTH/2 - BALL_RADIUS:
            if -NET_WIDTH/2 + BALL_RADIUS < ball.pos.y < NET_WIDTH/2 - BALL_RADIUS: #its going into the net TODO improve for small DT
                pass
            else:
                ball_velocity.x *= -1 # reflect the ball
                ball_velocity = inelastic_collision(ball_velocity, "table_boundary_x")
                ball.pos.x = np.sign(ball.pos.x) * (TABLE_LENGTH/2 - BALL_RADIUS) # set the ball position to the edge of the table
                most_recent_pawn = None

        if abs(ball.pos.y) >= TABLE_WIDTH/2 - BALL_RADIUS:
            ball_velocity.y *= -1 # reflect the ball
            ball_velocity = inelastic_collision(ball_velocity, "table_boundary_y")
            ball.pos.y = np.sign(ball.pos.y) * (TABLE_WIDTH/2 - BALL_RADIUS) # set the ball position to the edge of the table
            most_recent_pawn = None

        # Check if the ball if on the triangles
        for tri in triangles:
            if check_if_ball_is_on_triangle(ball, tri):
                modify_velocity_on_triangle(ball, ball_velocity)

        for border in borders:
            if check_if_ball_is_on_border(ball, border):
                modify_velocity_on_border(ball, ball_velocity)

        #check if players changes hand position, and move the rods. Also check for collisions with the pawns
        for player in players:
            
            player_pawns = pawns[player.team]
            player.move_hands(ball)

            opposing_posts = red_posts if player.team == 0 else blue_posts

            #calculate the displacement of each rod
            for i, rod_index in enumerate(player.hand_positions):
                displacement = player.calculate_rod_displacement(ball, ball_velocity, player_pawns, rod_index, displacement_error, opposing_posts)
                player.move_rod(rod_index, displacement, player_pawns)

            #change the color of the hand identifiers
            for i, hand_iden in enumerate(hand_identifiers[player.team*4 : (player.team+1) * 4]):
                change_hand_identifier_color(i, player, hand_iden)

            closest_rod_to_ball = np.argmin(abs(player.rod_positions - ball.pos.x))

            new_velocity_magnitude = player.get_velocity()

            rod_pawns = player_pawns[closest_rod_to_ball]

            for pawn in rod_pawns: # check for collisions with the closest rod to the ball
                if time_since_last_collision > 0.75:
                    most_recent_pawn = None #In case ball goes on a triangle and comes back
                if pawn == most_recent_pawn:
                    continue
                reflection_normal = check_ball_pawn_collision(ball, pawn)

                if reflection_normal is not None: # collision detected
                    time_since_last_collision = 0

                    relative_incoming_angle = reflection_normal.diff_angle(vector(1 - 2*player.team, 0, 0)) # pi: from the back, pi/2 on top or bottom, 0 from the front

                    # ball cannot be controlled if the player's hand is not on the rod or if the player is not available to control the ball
                    if closest_rod_to_ball not in player.hand_positions or not is_hand_available(closest_rod_to_ball, player.transition_cooldown):
                        is_ball_controlled = False

                    else: # check where the ball is coming from
                        is_ball_controlled = player.is_ball_controlled(mag(ball_velocity), relative_incoming_angle)

                    can_pass = player.can_pass(is_ball_controlled)

                    if is_ball_controlled:
                        if can_pass and closest_rod_to_ball != 0: # goalkeeper cannot pass
                            ball_velocity = pass_ball(pawn, rod_pawns, new_velocity_magnitude)
                            ball.pos.x = pawn.pos.x
                        else:
                            ball_velocity = controlled_shot(closest_rod_to_ball, ball, pawns, player, opposing_posts, new_velocity_magnitude, ball_velocity)
                    else:
                        if relative_incoming_angle == np.pi/2: # ball is coming from the top or bottom of the pawn (from a pass)
                            ball_velocity = diffuse_reflection(ball_velocity)
                        else:
                            ball_velocity = specular_reflection(ball_velocity, reflection_normal)

                    most_recent_pawn = pawn
                    displacement_error = np.random.normal(0, -1.6*player.reflexes/DT/100 + 20) #divided by DT and reflex multiplier
                    break

        net_number = 0
        for net in [net_blue, net_red]:
            if is_ball_in_net(ball, net):
                if net_number == 0:
                    gameOver = update_score(1, score, score_label)
                    time.sleep(0.5)
                    ball, ball_velocity = faceoff(ball)
                    time.sleep(0.5)
                else:
                    gameOver = update_score(0, score, score_label)
                    time.sleep(0.5)
                    ball, ball_velocity = faceoff(ball)
                    time.sleep(0.5)
            net_number += 1

    data = []
    with open(outputfile, 'r') as file:
        data = json.load(file)


    # Write the JSON data to a file
    data.append({
        "game_score": score,
        "simulation_duration" : simulation_time,
        "time" : time.strftime("%Y-%m-%d %H:%M:%S")
    })

    with open(outputfile, 'w') as json_file:
        json.dump(data, json_file, indent = 4)

    scene.delete() 

def set_seed(seed : int):
    np.random.seed(seed)

if __name__ == '__main__':
    manually_defined_path = "./simulation_results/_temp.json"
    manually_defined_seed = None

    if manually_defined_path is None:
        pass
    else:
        # If seed is given, set it up
        if manually_defined_seed is not None:
            np.random.seed(manually_defined_seed)
            print("Simulation started with seed:", manually_defined_seed)
        else:
            # If no seed is given, set a random seed
            auto_generated_seed = int(time.time())
            np.random.seed(auto_generated_seed)
            print("Simulation started with seed:", auto_generated_seed)

        # Execute simulation
        main(manually_defined_path)
else:
    pass