from vpython import sphere, vector, box
from config import *
import math
import numpy as np

class Player():
    """
    Class representing a player in the babyfoot game.
    Each player has a team (0=blue, 1=red), stats (reflexes, transition speed, shot power, technique), and a strategy.
    """

    ALL_ROD_POSITIONS = [BLUE_ROD_POSITIONS, RED_ROD_POSITIONS]

    def __init__(self, team, reflexes, transition_speed, strength, technique, strategy):
        #each of the four stats are on a scale from 1-10
        self.team = team #0 = blue, 1 = red
        self.reflexes = reflexes/10 
        self.transition = transition_speed
        self.force = strength
        self.technique = technique
        self.strategy = strategy  # 0 = gk all time, 1 = opportunistic attack, 2 = def all time, 3 = never midfield
        self.hand_positions = [0, 1]  #[rod left hand, rod right hand]

        self.rod_positions = self.ALL_ROD_POSITIONS[self.team] #get the rod positions for the team

    
    def moveHands(self, ball : sphere):
        ball_section = 0 #0 = defensive net to mid, 1 = mid to att, 2 = att to offensive net

        if self.team == 0:
            if ball.pos.x > self.rod_positions[3]: #ball in attack
                ball_section = 2
            elif ball.pos.x > self.rod_positions[2]: #ball in midfield
                ball_section = 1
        else:
            if ball.pos.x < self.rod_positions[3]:
                ball_section = 2
            elif ball.pos.x < self.rod_positions[2]:
                ball_section = 1

        if self.strategy == 0: #gk all the time
            hand_pos = [[0, 1], [0, 2], [0, 3]][ball_section]
        elif self.strategy == 1: #opportunistic attack
            hand_pos = [[0, 1], [0, 2], [2, 3]][ball_section]
        elif self.strategy == 2: #def all the time
            hand_pos = [[0, 1], [1, 2], [1, 3]][ball_section]
        else: #never midfielders
            hand_pos = [[0, 1], [0, 1], [0, 3]][ball_section]

        if hand_pos != self.hand_positions:
            self.hand_positions = hand_pos
            return True #returns True quand les mains ont changé
        
        self.hand_positions = hand_pos
        return False #return False quand les mains n'ont pas changé

    def calculate_rod_displacement(self, ball : sphere, ball_velocity : vector, pawns: list[list[box]], hand_position: int):
        rod_pos_x = self.rod_positions[hand_position]
        rod_pawns = pawns[hand_position]
        
        delta_x = ball.pos.x - rod_pos_x
        predicted_hit_y = delta_x * ball_velocity.y/ball_velocity.x + ball.pos.y
        
        if (self.team == 0 and ball_velocity.x > 0) or (self.team == 1 and ball_velocity.x < 0):
            return 0 # ball goes towards opposing net

        elif (self.team == 0 and ball.pos.x < rod_pos_x) or (self.team == 1 and ball.pos.x > rod_pos_x):
            return 0 # la balle est derrière le joueur, donc bouge pas le pawn

        pawn_positions = np.array([pawn.pos.y for pawn in rod_pawns])
        nearest_pawn = rod_pawns[np.argmin(abs(pawn_positions - predicted_hit_y))]

        delta_y = predicted_hit_y - nearest_pawn.pos.y

        return max(-self.reflexes, min(self.reflexes, delta_y))
        
    def move_rod(self, rod_number : int, displacement : int, pawns):
        #team Number: 0 for blue, 1 for red
        #rod Number : 0 = gk, 1 = def, 2 = mid, 3 = att
        #mmDisplacement is positive to go up, or negative to go down
        
        rod_to_move = pawns[rod_number]
        
        #check if player has hand on the rod
        if rod_number not in self.hand_positions:
            return None
        
        max_height = TABLE_WIDTH/2
        if rod_number == 0: #if gk
            max_height = NET_WIDTH/2
        
        legality = []
        for pawn in rod_to_move:
            if pawn.pos.y + displacement <= max_height and pawn.pos.y + displacement >= -max_height:
                legality.append(True)

        #if movement is legal, move all pawns on the rod
        if len(legality) == len(rod_to_move):
            for pawn in rod_to_move:
                pawn.pos += vector(0, displacement, 0)


