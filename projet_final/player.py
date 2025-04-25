from vpython import sphere, vector, box, color
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

        reflex_mutliplier = 25 # magic number to give the possible displacement per DT per reflexes stat point
        transition_multiplier = 450 #magic number to give the amount of time between transitions per DT per transition stat point

        self.reflexes = player_config["reflexes"]*DT*reflex_mutliplier # 0 to 10
        self.transition_time = player_config["transition_speed"]*DT*transition_multiplier # 0 to 10
        self.strength = player_config["strength"] # 0 to 10
        self.technique = player_config["technique"] # 0 to 10
        self.strategy = player_config["strategy"] # 0 = gk all time, 1 = opportunistic attack, 2 = def all time, 3 = never midfield
        self.transition_cooldown = [0, 0] #[cooldown iterations left for hand 1, for hand 2]
    
    def move_hands(self, ball : sphere):
        ball_section = 0 # intially set to defense
        
        if self.team == 0: # blue team
            if ball.pos.x >= self.rod_positions[3]: # ball further than attacker rod
                ball_section = 2
            elif ball.pos.x >= self.rod_positions[2]: #ball in midfield
                ball_section = 1

        else: # red team
            if ball.pos.x <= self.rod_positions[3]: # ball further than attacker rod
                ball_section = 2
            elif ball.pos.x <= self.rod_positions[2]: #ball in midfield
                ball_section = 1

        # print(self.team, ball_section, self.hand_positions)

        new_hand_positions = self.strategy_to_hand_positions[self.strategy][ball_section]

        hand_pos_has_changed = new_hand_positions != self.hand_positions
        if hand_pos_has_changed:
            for i in range(2):
                if self.hand_positions[i] != new_hand_positions[i]:
                    self.transition_cooldown[i] = round(self.transition_time)
            
        self.hand_positions = new_hand_positions

        return hand_pos_has_changed
    
    def calculate_rod_displacement(self, ball : sphere, ball_velocity : vector, pawns: list[list[box]], rod_number: int, hand_number : int, displacement_error):
        
        if self.transition_cooldown[hand_number] > 0:
            self.transition_cooldown[hand_number] -= 1
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

        if ball_velocity.x == 0: # ball direction is vertical, happens in passes
            return 0

        predicted_hit_y = delta_x * ball_velocity.y/ball_velocity.x + ball.pos.y

        # a noise is added
        predicted_hit_y += + displacement_error

        # bind predicted_hit_y to the table limits
        predicted_hit_y = max(-TABLE_WIDTH/2 + SPRING_LENGTH, min(TABLE_WIDTH/2 - SPRING_LENGTH, predicted_hit_y))

        if_list = [[ball_velocity.x, 0, rod_pos_x, ball.pos.x], [0, ball_velocity.x, ball.pos.x, rod_pos_x]][self.team]
        if (if_list[0] > if_list[1] and if_list[2] > if_list[3]): #velocity is towards opponent net, AND ball is behind the rod
            return self.pawn_ball_exit_displacement(rod_pawns, predicted_hit_y)
        elif (if_list[0] > if_list[1] or if_list[2] > if_list[3]): # velocity towards the opposing net, OR ball is behind the rod
            return 0

        if predicted_hit_y >= self.width_range:
            index_of_pawn = len(rod_pawns) - 1
        elif predicted_hit_y <= -self.width_range:
            index_of_pawn = 0
        else:
            for i, region in enumerate(self.pawn_y_ranges[rod_number]):
                if region[0] <= predicted_hit_y <= region[1]:
                    index_of_pawn = i
                    break
        
        try:
            pawn = rod_pawns[index_of_pawn]
        except:
            print(self.pawn_y_ranges)
            print(predicted_hit_y)
            print(rod_number)
            exit()
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
        return 400*(np.random.lognormal(np.log(self.strength), 5/(self.strength + 5), 1)[0] + 10)

    def is_ball_controlled(self, velocity_magnitude):
        velocity_correction = 1 - (velocity_magnitude / BALL_MAX_VELOCITY / 2) # 0.5 for a velocity max and 1 for a velocity min
        return np.random.rand() < (self.technique / 10 * velocity_correction) # technique 10 player with minimal velocity controlled 10/10 times
    
    def can_pass(self, velocity_magnitude):
        velocity_correction = 1 - (velocity_magnitude / BALL_MAX_VELOCITY / 2)
        return np.random.rand() < (self.technique / 10 / 2 * velocity_correction) # technique 10 player with minimal velocity passed 5/10 times

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
