# constants so we don't hardcode the values, which can get mixed up since they are strings
DIRECTION_NORTH = 'NORTH'
DIRECTION_EAST  = 'EAST'
DIRECTION_SOUTH = 'SOUTH'
DIRECTION_WEST  = 'WEST'

CELL_TYPE_ROOM  = ' '
CELL_TYPE_WALL  = '+'


class Cell:
    
    def __init__(self, x, y, cell_type=None, occupied=False):

        self.x = x
        self.y = y
        
        self.cell_type = cell_type
        self.occupied = occupied
        
    def is_free(self):
        if self.cell_type == CELL_TYPE_ROOM and self.occupied == False:
            return True
        return False
    
    

class Goal:
    
    def __init__(self, letter_id, location, is_satisfied=False):
        
        self.x = location.x
        self.y = location.y
        
        self.letter_id = letter_id
        self.is_satisfied = is_satisfied


# this class is incomplete, we need to add the level grid filled with cells, which will be implemented later on
# for now I've used a variable 'level' to represent the level array of cells
level_temp = [
    [Cell(0,0), Cell(1,0), Cell(2,0)],
    [Cell(0,1), Cell(1,1), Cell(2,1)],
    [Cell(0,2), Cell(1,2), Cell(2,2)]   
]


class Box:
    
    def __init__(self, letter_id, color, location, is_on_goal=False):
        
        self.x = location.x
        self.y = location.y
        
        self.letter_id = letter_id
        self.color = color
        self.is_on_goal = is_on_goal   # this parameter is optional, may help with heuristics
        
        
    def can_be_moved(self, direction):
        
        if direction == DIRECTION_NORTH and level_temp[self.x, self.y-1].is_free():
            return True
        elif direction == DIRECTION_EAST and level_temp[self.x+1, self.y].is_free():
            return True
        elif direction == DIRECTION_SOUTH and level_temp[self.x, self.y+1].is_free():
            return True
        elif direction == DIRECTION_WEST and level_temp[self.x-1, self.y].is_free():
            return True
        
        return False
        
        
    def move_box(self, direction):
        
        if direction == DIRECTION_NORTH:    
            level_temp[self.x, self.y].occupied = False
            self.y -= 1     
            level_temp[self.x, self.y].occupied = True
        
        elif direction == DIRECTION_EAST:
            level_temp[self.x, self.y].occupied = False
            self.x += 1
            level_temp[self.x, self.y].occupied = True
        
        elif direction == DIRECTION_SOUTH:
            level_temp[self.x, self.y].occupied = False
            self.y += 1
            level_temp[self.x, self.y].occupied = True
        
        elif direction == DIRECTION_WEST:
            level_temp[self.x, self.y].occupied = False
            self.x -= 1
            level_temp[self.x, self.y].occupied = True



# this class is incomplete, we need to add the level grid filled with cells, which will be implemented later on
# for now I've used a variable 'level' to represent the level array of cells

class Agent:
    
    def __init__(self, num_id, color, location):
        
        self.x = location.x
        self.y = location.y
        
        self.num_id = num_id
        self.color = color
        
        
    def current_location(self):
        return zip(location.x, location.y)
    
    
    def move(self, direction):
        
        # we set the current cell to the free state, move the agent to the new cell, 
        # and mark the new cell state as occupied
        
        if direction == DIRECTION_NORTH:    
            level_temp[self.x, self.y].occupied = False
            self.y -= 1     
            level_temp[self.x, self.y].occupied = True
        
        elif direction == DIRECTION_EAST:
            level_temp[self.x, self.y].occupied = False
            self.x += 1
            level_temp[self.x, self.y].occupied = True
        
        elif direction == DIRECTION_SOUTH:
            level_temp[self.x, self.y].occupied = False
            self.y += 1
            level_temp[self.x, self.y].occupied = True
        
        elif direction == DIRECTION_WEST:
            level_temp[self.x, self.y].occupied = False
            self.x -= 1
            level_temp[self.x, self.y].occupied = True
            
            
    def can_move(self, direction):
        
        if direction == DIRECTION_NORTH and level_temp[self.x, self.y-1].is_free():
            return True
        elif direction == DIRECTION_EAST and level_temp[self.x+1, self.y].is_free():
            return True
        elif direction == DIRECTION_SOUTH and level_temp[self.x, self.y+1].is_free():
            return True
        elif direction == DIRECTION_WEST and level_temp[self.x-1, self.y].is_free():
            return True
        
        return False
    
    
    def move_box(self, dir_agent, target_box, dir_box):
        # both push and pull, no difference in code 
        
        #first, we need to make sure both box and agent can move to free spaces 
        
        box_can_move = target_box.can_be_moved(dir_box)
        agent_can_move = self.can_move(dir_agent)
        
        if box_can_move and agent_can_move
            
            self.move(dir_agent)
            target_box.move_box(dir_box)

