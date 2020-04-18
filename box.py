
import location

class Box:
    def __init__(self,location,color,letter):
        self.location = location
        self.color = color
        self.letter = letter
        
    def __str__(self) :
        return str(self.location)+'\nColor : '+self.color+'\nLetter : '+self.letter