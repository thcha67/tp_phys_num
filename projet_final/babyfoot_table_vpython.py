from vpython import canvas, box, sphere, vector, color, rate
import numpy as np
import math

table_length = 20
table_width = 10
def_pos = [-table_width/5, table_width/5]
mid_pos = [-2*table_width/5, -table_width/5, 0, table_width/5, 2*table_width/5]
att_pos = [-3*table_width/10, 0, 3*table_width/10]

rod_positions = [-table_length/2+1, -table_length/3, -table_length/20, table_length/5]
pwn_sz = [0.4, 0.8]
ball_initial_pos, ball_initial_velocity, ball_radius = [0, 0], 4, 0.2
ball_max_velocity, ball_min_velocity = 15, 2

net_thickness, net_height, net_depth = 0.1, 3, 0.5
rod_thickness = 0.1

# Simulation parameters
dt = 0.02

# Set up the scene
scene = canvas(title='Babyfoot Table', width=800, height=600)

# Create the table
table = box(pos=vector(0, 0, 0), size=vector(table_length, table_width, 0.1), color=color.green)

# Create the rods
rods = []
for pos in rod_positions:
    rods.append(box(pos=vector(pos, 0, 0.15), size=vector(rod_thickness, table_width, rod_thickness), color=color.gray(0.5)))
for pos in [-p for p in rod_positions]:
    rods.append(box(pos=vector(pos, 0, 0.15), size=vector(rod_thickness, table_width, rod_thickness), color=color.gray(0.5)))


# Create the players
players = []

# goalkeepers
players.append(box(pos=vector(rod_positions[0], 0, 0.15), size=vector(pwn_sz[0], pwn_sz[1], 0.1), color=color.blue)) #blue
players.append(box(pos=vector(-rod_positions[0], 0, 0.15), size=vector(pwn_sz[0], pwn_sz[1], 0.1), color=color.red)) #red

# defenders
for y in def_pos:
    players.append(box(pos=vector(rod_positions[1], y, 0.15), size=vector(pwn_sz[0], pwn_sz[1], 0.1), color=color.blue)) #blue
for y in def_pos:
    players.append(box(pos=vector(-rod_positions[1], y, 0.15), size=vector(pwn_sz[0], pwn_sz[1], 0.1), color=color.red)) #red

# midfielders
for y in mid_pos:
    players.append(box(pos=vector(rod_positions[2], y, 0.15), size=vector(pwn_sz[0], pwn_sz[1], 0.1), color=color.blue)) #blue
for y in mid_pos:
    players.append(box(pos=vector(-rod_positions[2], y, 0.15), size=vector(pwn_sz[0], pwn_sz[1], 0.1), color=color.red)) #red

# attackers
for y in att_pos:
    players.append(box(pos=vector(rod_positions[3], y, 0.15), size=vector(pwn_sz[0], pwn_sz[1], 0.1), color=color.blue)) #blue
for y in att_pos:
    players.append(box(pos=vector(-rod_positions[3], y, 0.15), size=vector(pwn_sz[0], pwn_sz[1], 0.1), color=color.red)) #red

# Create the ball at the specified position
ball = sphere(pos=vector(ball_initial_pos[0], ball_initial_pos[1], 0.15), radius=ball_radius, color=color.white)
ball_velocity = vector(2*ball_initial_velocity, -0.5*ball_initial_velocity, 0)


# Create the nets behind each goalkeeper
net_blue = box(pos=vector(-table_length/2-net_depth/2, 0, 0.15), size=vector(net_depth, net_height, net_thickness), color=color.white)
net_red = box(pos=vector(table_length/2+net_depth/2, 0, 0.15), size=vector(net_depth, net_height, net_thickness), color=color.white)


# Add a flag to check if the window is closed
running = True

def check_window_closed():
    global running
    if scene.visible == False:
        running = False

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
