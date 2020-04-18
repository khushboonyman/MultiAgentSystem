import location    


Dir = {'E','W','N','S'}
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
        if self.location !=agtto and agtto.free() and not self.location.free() and self.location.neighbor(agtto) :
            move_dir_agent = TranslateToDir(self.location,agtto)
            self.location.assign(' ')
            self.location = agtto
            self.location.assign(self.number)
            return 'Move('+move_dir_agent+')'
        return 'NoOp'
               
    def Push(self,box,boxto):
        if ( self.location !=boxto and box.location != boxto and boxto.free() and not self.location.free() 
        and self.location.neighbor(box.location) and box.location.neighbor(boxto) and self.color == box.color) :
            move_dir_agent = TranslateToDir(self.location,box.location)
            move_dir_box = TranslateToDir(box.location,boxto)
            self.location.assign(' ')
            self.location = box.location
            self.location.assign(self.number)
            box.location = boxto
            box.location.assign(box.letter)
            return 'Push('+move_dir_agent+','+move_dir_box+')'
        return 'NoOp' 
    
    def Pull(self,agtto,box):
        if ( self.location !=agtto and box.location != self.location and agtto.free() and not box.location.free() 
        and self.location.neighbor(agtto) and box.location.neighbor(self.location) and self.color == box.color) :
            move_dir_agent = TranslateToDir(self.location,agtto)
            curr_dir_box = TranslateToDir(self.location,box.location)
            box.location.assign(' ')
            box.location = self.location
            box.location.assign(box.letter)
            self.location = agtto
            self.location.assign(self.number)
            return 'Pull('+move_dir_agent+','+curr_dir_box+')'
        return 'NoOp'
    
    
    
                
            
        
            
            
            
        
        
    