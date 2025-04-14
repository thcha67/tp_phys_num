from vpython import sphere, vector, box
from config import *

class player():
    
    def __init__(self, reflexes, vitesseTransition, forceFrappe, technique, preferedStrategy):
        #each of the four stats are on a scale from 1-10
        self.reflexes = reflexes
        self.transition = vitesseTransition
        self.force = forceFrappe
        self.technique = technique
        self.strategy = preferedStrategy  # 0 = gk all time, 1 = opportunistic attack, 2 = def all time, 3 = never midfield
        self.handPositions = [0, 1]  #[rod left hand, rod right hand]

    
    def moveHands(self, ball : sphere, teamNumber : int):
        #teamNumber: 0 = blue, 1 = red
        rod_positions = [BLUE_ROD_POSITIONS, RED_ROD_POSITIONS][teamNumber]

        ball_section = 0 #0 = defensive net to mid, 1 = mid to att, 2 = att to offensive net
        if teamNumber == 0:
            if ball.pos.x > rod_positions[3]: #ball in attack
                ball_section = 2
            elif ball.pos.x > rod_positions[2]: #ball in midfield
                ball_section = 1
        else:
            if ball.pos.x < rod_positions[3]:
                ball_section = 2
            elif ball.pos.x < rod_positions[2]:
                ball_section = 1

        if self.strategy == 0: #gk all the time
            handPos = [[0, 1], [0, 2], [0, 3]][ball_section]
        elif self.strategy == 1: #opportunistic attack
            handPos = [[0, 1], [0, 2], [2, 3]][ball_section]
        elif self.strategy == 2: #def all the time
            handPos = [[0, 1], [1, 2], [1, 3]][ball_section]
        else: #never midfielders
            handPos = [[0, 1], [0, 1], [0, 3]][ball_section]

        if handPos != self.handPositions:
            self.handPositions = handPos
            return True #returns True quand les mains ont changé
        
        self.handPositions = handPos
        return False #return False quand les mains n'ont pas changé

    def moveRodAmount(self, ball : sphere, ball_velocity : vector, teamNumber : int, pawns):
        #teamNumber: 0 = blue, 1 = red
        #pawns = [blue_pawns, red_pawns]
        rod_positions = [BLUE_ROD_POSITIONS, RED_ROD_POSITIONS][teamNumber]
        pawns = pawns[teamNumber] #juste les pawns de la bonne équipe
        
        mmDisplacement = []
        for hand in self.handPositions:
            rod_pos_x = rod_positions[hand]
            delta_x = ball.pos.x - rod_pos_x
            rod_pawns = pawns[hand]

            if ball_velocity.x * delta_x > 0: #s'ils ont pas le même signe!
                mmDisplacement.append(0) #la balle ne se déplace pas vers le joueur, donc bouge pas le pawn
                continue

            if ball_velocity.x > 0 and teamNumber == 0:
                mmDisplacement.append(0)
                continue
            elif ball_velocity.x < 0 and teamNumber == 1:
                mmDisplacement.append(0)
                continue
            
            future_ball_position_at_rod= delta_x * ball_velocity.y / ball_velocity.x + ball.pos.y
            index_of_closest_pawn, distance_closest_pawn = 0, 1000
            for i in range(len(rod_pawns)):
                if rod_pawns[i].pos.y - future_ball_position_at_rod < distance_closest_pawn:
                    index_of_closest_pawn = i
            

            mmDisplacement.append(min(future_ball_position_at_rod - rod_pawns[index_of_closest_pawn].pos.y, self.reflexes))
        
        return mmDisplacement
        


