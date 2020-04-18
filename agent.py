from location import *
from state import *    

def TranslateToDir(locfrom,locto):
    if locfrom.x == locto.x :
        if locto.y == locfrom.y-1 :
            return 'W'
        else :
            return 'E'
    else :
        if locto.x == locfrom.x-1 :
            return 'N'
        else :
            return 'S'
                    
class Agent :
    def __init__(self,location,color,number):
        self.location = location
        self.color = color
        self.number = number
        
    def __str__(self) :
        return str(self.location)+'\nColor : '+self.color+'\nLetter : '+self.number
    
    def Move(self,agtto):
        if (self.location !=agtto and agtto in CurrentState.FreeCells and self.location not in CurrentState.FreeCells and 
        agtto in CurrentState.Neighbours[self.location]) :
            
            move_dir_agent = TranslateToDir(self.location,agtto)
            self.location.assign(' ')
            CurrentState.FreeCells.append(self.location)
            self.location = agtto
            self.location.assign(self.number)
            CurrentState.FreeCells.remove(self.location)
            return 'Move('+move_dir_agent+')'
        
        return 'NoOp'
               
    def Push(self,box,boxto):
        if (self.location !=boxto and box.location != boxto and boxto in CurrentState.FreeCells and 
        self.location not in CurrentState.FreeCells and self.color == box.color and 
        box.location in CurrentState.Neighbours[self.location] and boxto in CurrentState.Neighbours[box.location]) :
        
            move_dir_agent = TranslateToDir(self.location,box.location)
            move_dir_box = TranslateToDir(box.location,boxto)
            self.location.assign(' ')
            CurrentState.FreeCells.append(self.location)
            self.location = box.location
            self.location.assign(self.number)
            box.location = boxto
            box.location.assign(box.letter)
            CurrentState.FreeCells.remove(boxto)
            return 'Push('+move_dir_agent+','+move_dir_box+')'
        
        return 'NoOp' 
    
    def Pull(self,agtto,box):
        if ( self.location != agtto and box.location != self.location and agtto in CurrentState.FreeCells and 
        box.location not in CurrentState.FreeCells and self.color == box.color and 
        agtto in CurrentState.Neighbours[self.location] and self.location in CurrentState.Neighbours[box.location]) : 
            
            move_dir_agent = TranslateToDir(self.location,agtto)
            curr_dir_box = TranslateToDir(self.location,box.location)
            box.location.assign(' ')
            CurrentState.FreeCells.append(box.location)
            box.location = self.location
            box.location.assign(box.letter)
            self.location = agtto
            self.location.assign(self.number)
            CurrentState.FreeCells.append(agtto)
            return 'Pull('+move_dir_agent+','+curr_dir_box+')'
        
        return 'NoOp'
    
    
    
                
            
        
            
            
            
        
        
    