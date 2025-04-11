from vpython import canvas, box, sphere, vector, color, rate, mag
import numpy as np
import time

#toutes les mesures sont en mm (x, y, z)

table_length, table_width = 1140, 700
pwn_sz = np.array([11, 21, 1])

sep_def, sep_mid, sep_att = 335, 122, 215  #separation head to head between players

gk_pos = [0]
def_pos = [-sep_def/2, sep_def/2]
mid_pos = [-2*sep_mid, -sep_mid, 0, sep_mid, 2*sep_mid]
att_pos = [-sep_att, 0, sep_att]

pwn_positions = [gk_pos, def_pos, mid_pos, att_pos]

blue_rod_positions = [-525, -375, -72, 228] # gk, def, mid, att
red_rod_positions = [525, 375, 72, -228]

ball_initial_pos, ball_initial_velocity, ball_initial_dir = [0, 0], 100, [2, 0.5]
ball_max_velocity, ball_min_velocity, ball_radius = 15, 2, 16

net_thickness, net_height, net_depth = 0.1, 204, 40
rod_thickness = 5

# Simulation parameters
dt = 0.02

# Set up the scene
scene = canvas(title='Babyfoot Table', width=800, height=600)

# Create the table
table = box(pos=vector(0, 0, 0), size=vector(table_length, table_width, 0.1), color=color.green)

# Create the rods
rods = [
    box(pos=vector(rod_position, 0, 0.15), size=vector(rod_thickness, table_width, 0.1), color=color.gray(0.5))
    for rod_position in blue_rod_positions + red_rod_positions
]

# Create the players
pwns: list[box] = []

# blue
for i, rod_pos in enumerate(blue_rod_positions):
    for pwn_pos in pwn_positions[i]:
        pwns.append(box(pos=vector(rod_pos, pwn_pos, 0.15), size=vector(pwn_sz[0], pwn_sz[1], 1), color=color.blue))

# red
for i, rod_pos in enumerate(red_rod_positions):
    for pwn_pos in pwn_positions[i]:
        pwns.append(box(pos=vector(rod_pos, pwn_pos, 0.15), size=vector(pwn_sz[0], pwn_sz[1], 1), color=color.red))


# Create the ball at the specified position
ball = sphere(pos=vector(ball_initial_pos[0], ball_initial_pos[1], 0.15), radius=ball_radius, color=color.white)
ball_initial_dir = [element / np.sqrt(ball_initial_dir[0]**2 + ball_initial_dir[1]**2) for element in ball_initial_dir]
ball_velocity = vector(ball_initial_dir[0]*ball_initial_velocity, ball_initial_dir[1]*ball_initial_velocity, 0)


# Create the nets behind each goalkeeper
net_blue = box(pos=vector(-table_length/2-net_depth/2, 0, 0.15), size=vector(net_depth, net_height, net_thickness), color=color.white)
net_red = box(pos=vector(table_length/2+net_depth/2, 0, 0.15), size=vector(net_depth, net_height, net_thickness), color=color.white)
nets = [net_blue, net_red]



maximal_dist_of_collision = ball_radius + np.sqrt(pwn_sz[0]**2 + pwn_sz[1]**2) #maximal distance between the ball and the player to be considered as a collision

print("Press 'q' to quit the simulation.")


# corner angles
corner_angles = [0.983, 1.337, np.pi-1.337, np.pi-0.983] # in radians

most_recent_pawn = None
while True:
    rate(300)
    # Move the ball
    ball.pos += ball_velocity * dt

    # Check for collisions with table boundaries
    if abs(ball.pos.x) > table_length/2:
        ball_velocity.x *= -1
        most_recent_pawn = None
    if abs(ball.pos.y) > table_width/2:
        ball_velocity.y *= -1
        most_recent_pawn = None

    # for pwn in pwns:
    #     if abs(ball.pos.x - pwn.pos.x) < (ball.radius + pwn.size.x / 2) and abs(ball.pos.y - pwn.pos.y) < (ball.radius + pwn.size.y / 2):
    #         ball_velocity.x *= -(np.random.uniform(0.2, 2))
    #         if abs(ball_velocity.x) > ball_max_velocity:
    #             ball_velocity.x = ball_max_velocity*math.copysign(1, ball_velocity.x)
    #         elif abs(ball_velocity.x) < ball_min_velocity:
    #             ball_velocity.x = ball_min_velocity*math.copysign(1, ball_velocity.x)

    # Check for collisions with players
    
    for pwn in pwns:
        pawn_to_ball_vct = pwn.pos - ball.pos
        pawn_to_ball_distance = mag(pawn_to_ball_vct)
        if pawn_to_ball_distance < maximal_dist_of_collision and most_recent_pawn != pwn:
            if abs(ball.pos.x - pwn.pos.x) < (ball.radius + pwn.size.x / 2) and abs(ball.pos.y - pwn.pos.y) < (ball.radius + pwn.size.y / 2):
                x_pos, y_pos = -pawn_to_ball_vct.x, -pawn_to_ball_vct.y
                incident_angle = np.arctan2(y_pos, x_pos)
                
                if ((corner_angles[0] < abs(incident_angle) < corner_angles[1]) or
                    (corner_angles[2] < abs(incident_angle) < corner_angles[3])):
                    print("corner")
                elif corner_angles[1] < abs(incident_angle) < corner_angles[2]:
                    print("y_rebound")
                    ball_velocity.y *= -1
                else:
                    print("x_rebound")
                    ball_velocity.x *= -1
                time.sleep(1)
                most_recent_pawn = pwn
            break
    
    for net in nets:
        if abs(ball.pos.x - net.pos.x) < (ball.radius + net.size.x / 2) and abs(ball.pos.y - net.pos.y) < (ball.radius + net.size.y / 2):
            print("GOAL")