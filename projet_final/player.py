from vpython import sphere, vector, box, color, arrow, mag
from config import *
import time
import numpy as np

class Player():
    """
    Class representing a player in the babyfoot game.
    Each player has a team (0=blue, 1=red), stats (reflexes, transition speed, shot power, technique), and a strategy.
    """

    ALL_ROD_POSITIONS = [BLUE_ROD_POSITIONS, RED_ROD_POSITIONS]

    strategy_to_hand_positions = [
        [[0, 1], [0, 2], [0, 3]], # gk all the time
        [[0, 1], [0, 2], [2, 3]], # opportunistic attack
        [[0, 1], [1, 2], [1, 3]], # def all the time
        [[0, 1], [0, 1], [0, 3]], # never midfielders ):
    ]
    transition_zone_amount = 80

    eff_tab_width = TABLE_WIDTH-2*SPRING_LENGTH
    width_range = eff_tab_width/2
    pawn_y_ranges = [
        [[-NET_WIDTH/2, NET_WIDTH/2]],
        [[-width_range, -width_range+eff_tab_width/2], [-width_range+eff_tab_width/2, width_range]],
        [[-width_range, -width_range+eff_tab_width/5], [-width_range+eff_tab_width/5, -width_range+2*eff_tab_width/5], [-width_range+2*eff_tab_width/5, -width_range+3*eff_tab_width/5], [-width_range+3*eff_tab_width/5, -width_range+4*eff_tab_width/5], [-width_range+4*eff_tab_width/5, width_range]],
        [[-width_range, -width_range+eff_tab_width/3], [-width_range+eff_tab_width/3, -width_range+2*eff_tab_width/3], [-width_range+2*eff_tab_width/3, width_range]]]

    def __init__(self, team):
        #each of the four stats are on a scale from 1-10
        self.team = team #0 = blue, 1 = red
        self.color = color.blue if team == 0 else color.red
        self.load_player_config()
        self.hand_positions = [0, 1]  #[rod left hand, rod right hand]
        self.rod_positions = np.array(self.ALL_ROD_POSITIONS[self.team]) #get the rod positions for the team

    def load_player_config(self):
        with open(f"player{self.team}.json", "r") as f:
            player_config = json.load(f)

        reflex_mutliplier = 25*10 # magic number to give the possible displacement per DT per reflexes stat point

        self.reflexes = player_config["reflexes"]*DT*reflex_mutliplier # 0 to 10
        self.transition_speed = player_config["transition_speed"]# 0 to 10
        self.strength = player_config["strength"] # 0 to 10
        self.technique = player_config["technique"] # 0 to 10
        self.strategy = player_config["strategy"] # 0 = gk all time, 1 = opportunistic attack, 2 = def all time, 3 = never midfield
        self.transition_cooldown = [0, 0, 0, 0] #[rod 0, rod 1, rod 2, rod 3]
    
    def move_hands(self, ball : sphere):
        ball_section = 0 # intially set to defense
        
        if self.team == 0: # blue team
            if ball.pos.x >= self.rod_positions[3] - self.transition_zone_amount: # ball further than attacker rod
                ball_section = 2
            elif ball.pos.x >= self.rod_positions[2] - self.transition_zone_amount: #ball in midfield
                ball_section = 1

        else: # red team
            if ball.pos.x <= self.rod_positions[3] + self.transition_zone_amount: # ball further than attacker rod
                ball_section = 2
            elif ball.pos.x <= self.rod_positions[2] + self.transition_zone_amount: #ball in midfield
                ball_section = 1

        new_hand_positions = self.strategy_to_hand_positions[self.strategy][ball_section]

        hand_pos_has_changed = new_hand_positions != self.hand_positions
        if hand_pos_has_changed:
            for i in range(2):
                if self.hand_positions[i] != new_hand_positions[i]:
                    new_transition_time = np.random.normal(1-self.transition_speed/20, 0.1)
                    self.transition_cooldown[new_hand_positions[i]] = new_transition_time
                    print(self.team, self.transition_cooldown)
            
        self.hand_positions = new_hand_positions

        return hand_pos_has_changed
    
    def calculate_rod_displacement(self, ball : sphere, ball_velocity : vector, pawns: list[list[box]], rod_number: int, displacement_error, posts):
        
        if self.transition_cooldown[rod_number] > 0:
            self.transition_cooldown[rod_number] -= DT
            return 0
        
        rod_pos_x = self.rod_positions[rod_number]
        
        rod_pawns = pawns[rod_number]
        
        if rod_number == 0:
            delta_y = ball.pos.y - rod_pawns[0].pos.y
            gk_displacement = max(-self.reflexes, min(self.reflexes, delta_y))
            if self.is_gk_displacement_allowed(rod_pawns, gk_displacement):
                return gk_displacement
            else:
                return 0
            
        delta_x = rod_pos_x - ball.pos.x

        if delta_x == 0: # ball is on the rod, then wait for the pass
            return 0

        if ball_velocity.x == 0: # ball direction is vertical, happens in passes, then follow the ball
            if rod_number == 1: # defender does not simply follow the ball, he postions to intercept a shot to the center of the net
                net_center = (posts[0].pos + posts[1].pos) / 2
                ball_to_net_center = net_center - ball.pos
                # normalize the vector to get the direction
                ball_to_net_center = ball_to_net_center / mag(ball_to_net_center)
                
                predicted_hit_y = ball.pos.y + ball_to_net_center.y * (ball.pos.x - rod_pos_x)
                # arrow(pos=ball.pos, axis=ball_to_net_center*100, color=color.red, shaftwidth=2)
                # time.sleep(0.1)
            else:
                predicted_hit_y = ball.pos.y - rod_pawns[0].pos.y
        else: # ball is coming towrards the rod, estimate where it will hit the rod
            predicted_hit_y = delta_x * ball_velocity.y/ball_velocity.x + ball.pos.y

        # a noise is added
        #predicted_hit_y += + displacement_error

        # bind predicted_hit_y to the table limits
        predicted_hit_y = max(-TABLE_WIDTH/2 + SPRING_LENGTH, min(TABLE_WIDTH/2 - SPRING_LENGTH, predicted_hit_y))

        if predicted_hit_y >= self.width_range:
            index_of_pawn = len(rod_pawns) - 1
        elif predicted_hit_y <= -self.width_range:
            index_of_pawn = 0
        else:
            for i, region in enumerate(self.pawn_y_ranges[rod_number]):
                if region[0] <= predicted_hit_y <= region[1]:
                    index_of_pawn = i
                    break
        
        pawn = rod_pawns[index_of_pawn]
    
        delta_y = predicted_hit_y - pawn.pos.y
        displacement = max(-self.reflexes, min(self.reflexes, delta_y))

        if self.is_displacement_allowed(rod_pawns, displacement):
            return displacement
        else:
            return 0
    
    def is_displacement_allowed(self, rod_pawns, displacement):
        max_position = TABLE_WIDTH / 2 - SPRING_LENGTH
        for pawn in rod_pawns:
            if pawn.pos.y + displacement > max_position or pawn.pos.y + displacement < -max_position:
                return False
        return True
    
    def is_gk_displacement_allowed(self,rod_pawns, displacement):
        max_position = NET_WIDTH / 2
        if rod_pawns[0].pos.y + displacement > max_position or rod_pawns[0].pos.y + displacement < -max_position:
            return False
        return True

    def move_rod(self, rod_number : int, displacement : int, pawns):
        #rod Number : 0 = gk, 1 = def, 2 = mid, 3 = att

        rod_to_move = pawns[rod_number]
        
        for pawn in rod_to_move:
            pawn.pos.y += displacement

    def get_velocity(self):
        return 300*(np.random.lognormal(np.log(self.strength), 5/(self.strength + 5), 1)[0] + 10)

    def is_ball_controlled(self, velocity_magnitude, relative_incoming_angle):
        if velocity_magnitude < 300:
            return True # 100% chance to control the ball if its slow enough
        
        velocity_correction = 1 - (velocity_magnitude / BALL_MAX_VELOCITY / 2) # 0.5 for a velocity max and 1 for a velocity min
        
        is_ball_controlled = np.random.rand() < (self.technique / 10 * velocity_correction) 
        
        if relative_incoming_angle > np.pi/2: # ball is coming from the back of the pawn (back side or back corners)
            is_ball_controlled *= np.random.rand() < 0.25 # divide the probability of controlling the ball by 4

        return is_ball_controlled
    
    def can_pass(self, is_ball_controlled):
        return is_ball_controlled and np.random.rand() < 0.5 # 50% chance to pass or not when the ball is controlled

    def pawn_ball_exit_displacement(self, rod_pawns, predicted_hit_y):
        displacement = 0
        for pawn in rod_pawns:
            #check if pawn is blocking ball exit
            if predicted_hit_y - PAWN_SIZE[1]/2 - BALL_RADIUS - 5 < pawn.pos.y < predicted_hit_y + PAWN_SIZE[1]/2 + BALL_RADIUS + 5:
                if predicted_hit_y - pawn.pos.y < 0:
                    displacement = self.reflexes
                else:
                    displacement = -self.reflexes

                if not self.is_displacement_allowed(rod_pawns, displacement):
                    displacement = -displacement
        return displacement
