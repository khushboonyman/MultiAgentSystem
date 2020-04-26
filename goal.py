import location


class Goal:
    def __init__(self, location, color, letter):
        self.location = location
        self.color = color
        self.letter = letter

    def __str__(self):
        return str(self.location) + ', Color : ' + self.color + ', Letter : ' + self.letter

    def __eq__(self, other):
        if self.location == other.location and self.letter == other.letter and self.color == other.color:
            return True
        else:
            return False

    def __ne__(self, other):
        if self.location != other.location or self.letter != other.letter or self.color != other.color:
            return True
        else:
            return False
