from vpython import canvas, box, sphere, vector, color, rate
import numpy as np
import math

#toutes les mesures sont en mm

table_length, table_width = 1140, 700
pwn_sz = [11, 21]
sep_def, sep_mid, sep_att = 335, 122, 215  #separation head to head between players
def_pos = [-sep_def/2, sep_def/2]
mid_pos = [-2*sep_mid, -sep_mid, 0, sep_mid, 2*sep_mid]
att_pos = [-sep_att, 0, sep_att]

gk_rod_pos, def_rod_pos, mid_rod_pos, att_rod_pos = 45, 195, 498, 798 #position in mm from the gk end of the table
rod_positions = [-table_length/2+gk_rod_pos, -table_length/2+def_rod_pos, -table_length/2+mid_rod_pos, -table_length/2+att_rod_pos]
ball_initial_pos, ball_initial_velocity, ball_initial_dir = [0, 0], 50, [2, 0.5]
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
rods = []
for pos in rod_positions:
    rods.append(box(pos=vector(pos, 0, 0.15), size=vector(rod_thickness, table_width, 0.1), color=color.gray(0.5)))
for pos in [-p for p in rod_positions]:
    rods.append(box(pos=vector(pos, 0, 0.15), size=vector(rod_thickness, table_width, 0.1), color=color.gray(0.5)))

# Create the players
players = []

# goalkeepers
players.append(box(pos=vector(rod_positions[0], 0, 0.15), size=vector(pwn_sz[0], pwn_sz[1], 1), color=color.blue)) #blue
players.append(box(pos=vector(-rod_positions[0], 0, 0.15), size=vector(pwn_sz[0], pwn_sz[1], 1), color=color.red)) #red

# defenders
for y in def_pos:
    players.append(box(pos=vector(rod_positions[1], y, 0.15), size=vector(pwn_sz[0], pwn_sz[1], 1), color=color.blue)) #blue
for y in def_pos:
    players.append(box(pos=vector(-rod_positions[1], y, 0.15), size=vector(pwn_sz[0], pwn_sz[1], 1), color=color.red)) #red

# midfielders
for y in mid_pos:
    players.append(box(pos=vector(rod_positions[2], y, 0.15), size=vector(pwn_sz[0], pwn_sz[1], 1), color=color.blue)) #blue
for y in mid_pos:
    players.append(box(pos=vector(-rod_positions[2], y, 0.15), size=vector(pwn_sz[0], pwn_sz[1], 1), color=color.red)) #red

# attackers
for y in att_pos:
    players.append(box(pos=vector(rod_positions[3], y, 0.15), size=vector(pwn_sz[0], pwn_sz[1], 1), color=color.blue)) #blue
for y in att_pos:
    players.append(box(pos=vector(-rod_positions[3], y, 0.15), size=vector(pwn_sz[0], pwn_sz[1], 1), color=color.red)) #red

# Create the ball at the specified position
ball = sphere(pos=vector(ball_initial_pos[0], ball_initial_pos[1], 0.15), radius=ball_radius, color=color.white)
ball_initial_dir = [element / math.sqrt(ball_initial_dir[0]**2 + ball_initial_dir[1]**2) for element in ball_initial_dir]
ball_velocity = vector(ball_initial_dir[0]*ball_initial_velocity, ball_initial_dir[1]*ball_initial_velocity, 0)


# Create the nets behind each goalkeeper
net_blue = box(pos=vector(-table_length/2-net_depth/2, 0, 0.15), size=vector(net_depth, net_height, net_thickness), color=color.white)
net_red = box(pos=vector(table_length/2+net_depth/2, 0, 0.15), size=vector(net_depth, net_height, net_thickness), color=color.white)


# Add a flag to check if the window is closed
running = True

def check_window_closed():
    global running
    if scene.visible == False:
        running = False

def move_rod(color : str, rod_number : int, mov_amount : int):
    #for rod number, gk = 0, def = 1, mid = 2, att = 3
    #mov_amount in mm
    pass



while running:
    rate(50)
    check_window_closed()
    if not running:
        break
    # Move the ball
    ball.pos += ball_velocity * dt

    # Check for collisions with table boundaries
    if abs(ball.pos.x) > table_length/2:
        ball_velocity.x *= -1
    if abs(ball.pos.y) > table_width/2:
        ball_velocity.y *= -1

    # Check for collisions with players
    for player in players:
        if abs(ball.pos.x - player.pos.x) < (ball.radius + player.size.x / 2) and abs(ball.pos.y - player.pos.y) < (ball.radius + player.size.y / 2):
            ball_velocity.x *= -(np.random.uniform(0.2, 2))
            if abs(ball_velocity.x) > ball_max_velocity:
                ball_velocity.x = ball_max_velocity*math.copysign(1, ball_velocity.x)
            elif abs(ball_velocity.x) < ball_min_velocity:
                ball_velocity.x = ball_min_velocity*math.copysign(1, ball_velocity.x)
