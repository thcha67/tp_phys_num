from vpython import canvas, box, sphere, vector, color, rate, mag, text, label
import numpy as np
import time

#toutes les mesures sont en mm (x, y, z)

table_length, table_width = 1140, 700
pawn_sz = np.array([11, 21, 1])

sep_def, sep_mid, sep_att = 335, 122, 215  #separation head to head between players

gk_pos = [0]
def_pos = [-sep_def/2, sep_def/2]
mid_pos = [-2*sep_mid, -sep_mid, 0, sep_mid, 2*sep_mid]
att_pos = [-sep_att, 0, sep_att]

pawn_positions = [gk_pos, def_pos, mid_pos, att_pos]

blue_rod_positions = [-525, -375, -72, 228] # gk, def, mid, att
red_rod_positions = [525, 375, 72, -228]

ball_initial_pos, ball_initial_velocity, ball_initial_dir = [500, 0], 100, [1.3, 1.8]
ball_max_velocity, ball_min_velocity, ball_radius = 15, 2, 16

net_thickness, net_height, net_depth = 0.1, 204, 40
rod_thickness = 5
score = [0, 0]  #[blue team goals, red team goals]

# Simulation parameters
dt = 0.02

# Set up the scene
scene = canvas(title='Babyfoot Table', width=800, height=600)

# Create the table
table = box(pos=vector(0, 0, 0), size=vector(table_length, table_width, 0.1), color=color.green)


score_position = vector(0,table_width/2 + 100,10)
score_box = box(pos=score_position, size=vector(500,100,0), color=color.gray(0.5))
blue_label = label(pos=score_box.pos, text=f"{score[0]}    :   {score[1]}", xoffset=0, yoffset=0, space=score_box.size.x, height=25, border=4, font='sans')

# Create the rods
rods = [
    box(pos=vector(rod_position, 0, 0.15), size=vector(rod_thickness, table_width, 0.1), color=color.gray(0.5))
    for rod_position in blue_rod_positions + red_rod_positions
]

# Create the players
pawns: list[box] = []

# blue
for i, rod_pos in enumerate(blue_rod_positions):
    for pawn_pos in pawn_positions[i]:
        pawns.append(box(pos=vector(rod_pos, pawn_pos, 0.15), size=vector(pawn_sz[0], pawn_sz[1], 1), color=color.blue))

# red
for i, rod_pos in enumerate(red_rod_positions):
    for pawn_pos in pawn_positions[i]:
        pawns.append(box(pos=vector(rod_pos, pawn_pos, 0.15), size=vector(pawn_sz[0], pawn_sz[1], 1), color=color.red))


# Create the ball at the specified position
ball = sphere(pos=vector(ball_initial_pos[0], ball_initial_pos[1], 0.15), radius=ball_radius, color=color.white)
ball_initial_dir = [element / np.sqrt(ball_initial_dir[0]**2 + ball_initial_dir[1]**2) for element in ball_initial_dir]
ball_velocity = vector(ball_initial_dir[0]*ball_initial_velocity, ball_initial_dir[1]*ball_initial_velocity, 0)


# Create the nets behind each goalkeeper
net_blue = box(pos=vector(-table_length/2-net_depth/2, 0, 0.15), size=vector(net_depth, net_height, net_thickness), color=color.white)
net_red = box(pos=vector(table_length/2+net_depth/2, 0, 0.15), size=vector(net_depth, net_height, net_thickness), color=color.white)


blue_pawns = [[pawns[0]], [defender for defender in pawns[1:3]], [mid for mid in pawns[3:8]], [att for att in pawns[8:11]]]
red_pawns = [[pawns[11]], [defender for defender in pawns[12:14]], [mid for mid in pawns[14:19]], [att for att in pawns[19:22]]]
def move_rod(teamNumber : int, rodNumber : int, mmDisplacement : int):
    #team Number: 0 for blue, 1 for red
    #rod Number : 0 = gk, 1 = def, 2 = mid, 3 = att
    #mmDisplacement is positive to go up, or negative to go down
    
    rod_to_move = [blue_pawns, red_pawns][teamNumber][rodNumber]
    
    #check if movement is legal for all pawns
    legality = []
    if rodNumber == 0:
        for pawn in rod_to_move:
            if pawn.pos.y < net_height/2 and pawn.pos.y > -net_height/2:
                    legality.append(True)
    else:
        for pawn in rod_to_move:
            if pawn.pos.y < table_width/2 and pawn.pos.y > -table_width/2:
                    legality.append(True)
    
    #if movement is legal, move all pawns on the rod
    if len(legality) == len(rod_to_move):
        for pawn in rod_to_move:
            pawn.pos += vector(0, mmDisplacement, 0)

def update_score(teamNumber : int):
    score[teamNumber] = score[teamNumber] + 1
    blue_label.text = f"{score[0]}    :   {score[1]}"

# corner angles
maximal_dist_of_collision = ball_radius + np.sqrt(pawn_sz[0]**2 + pawn_sz[1]**2) #maximal distance between the ball and the player to be considered as a collision
corner_angles = [0.983, 1.337, np.pi-1.337, np.pi-0.983] # in radians
print("Press 'q' to quit the simulation.")

most_recent_pawn = None
recent_goal = False
while True:
    rate(600)
    # Move the ball
    ball.pos += ball_velocity * dt


    #ball_velocity.x, ball_velocity.y = ball_velocity.x*(1-dt/40), ball_velocity.y*(1-dt/40)

    # Check for collisions with table boundaries
    if abs(ball.pos.x) > table_length/2:
        ball_velocity.x *= -1
        most_recent_pawn = None
    if abs(ball.pos.y) > table_width/2:
        ball_velocity.y *= -1
        most_recent_pawn = None

    # for pawn in pawns:
    #     if abs(ball.pos.x - pawn.pos.x) < (ball.radius + pawn.size.x / 2) and abs(ball.pos.y - pawn.pos.y) < (ball.radius + pawn.size.y / 2):
    #         ball_velocity.x *= -(np.random.uniform(0.2, 2))
    #         if abs(ball_velocity.x) > ball_max_velocity:
    #             ball_velocity.x = ball_max_velocity*math.copysign(1, ball_velocity.x)
    #         elif abs(ball_velocity.x) < ball_min_velocity:
    #             ball_velocity.x = ball_min_velocity*math.copysign(1, ball_velocity.x)

    # Check for collisions with players

    for pawn in pawns:
        pawn_to_ball_vct = pawn.pos - ball.pos
        pawn_to_ball_distance = mag(pawn_to_ball_vct)
        if pawn_to_ball_distance < maximal_dist_of_collision and most_recent_pawn != pawn:
            if abs(ball.pos.x - pawn.pos.x) < (ball.radius + pawn.size.x / 2) and abs(ball.pos.y - pawn.pos.y) < (ball.radius + pawn.size.y / 2):
                recent_goal = False
                x_pos, y_pos = -pawn_to_ball_vct.x, -pawn_to_ball_vct.y
                center_to_center_angle = np.arctan2(y_pos, x_pos)
                
                if ((corner_angles[0] < abs(center_to_center_angle) < corner_angles[1]) or
                    (corner_angles[2] < abs(center_to_center_angle) < corner_angles[3])):
                    final_angle = 2*center_to_center_angle - np.arctan2(ball_velocity.y, ball_velocity.x)
                    # ball_velocity.x = ball_velocity.x * np.cos(final_angle)
                    # ball_velocity.y = ball_velocity.y * np.sin(final_angle) 
                    print("corner")

                elif corner_angles[1] < abs(center_to_center_angle) < corner_angles[2]:
                    print("y_rebound")
                    ball_velocity.y *= -1
                else:
                    print("x_rebound")
                    ball_velocity.x *= -1
                most_recent_pawn = pawn
            break
    
    net_number = 0
    for net in [net_blue, net_red]:
        if not recent_goal:
            if abs(ball.pos.x - net.pos.x) < (ball.radius + net.size.x / 2) and abs(ball.pos.y - net.pos.y) < (ball.radius + net.size.y / 2):
                if net_number == 0:
                    update_score(0)
                    recent_goal = True
                else:
                    update_score(1)
                    recent_goal = True
                print("GOAL")
                print(score)
        net_number += 1