"""
Created on Wed Apr 15 21:55:26 2020
@author :
"""

from location import *
from state import *
import sys
from queue import PriorityQueue


def TranslateToDir(locfrom, locto):
    if locfrom.x == locto.x:
        if locto.y == locfrom.y - 1:
            return 'W'
        else:
            return 'E'
    else:
        if locto.x == locfrom.x - 1:
            return 'N'
        else:
            return 'S'


class Agent:
    def __init__(self, location, color, number):
        self.location = location
        self.color = color
        self.number = number

    def __str__(self):
        return str(self.location) + ' Color : ' + self.color + ' Letter : ' + self.number

    def __hash__(self):
        return hash(str(self))
    
    def __lt__(self, other):
        if self.number < other.number :
            return True
        return False
    
    def __gt__(self, other):
        if self.number > other.number :
            return True
        return False

    def Move(self, agtto):
        if (self.location != agtto and agtto in CurrentState.FreeCells and self.location not in CurrentState.FreeCells and
            agtto in CurrentState.Neighbours[self.location]):
            move_dir_agent = TranslateToDir(self.location, agtto)
            self.location.free_cell()
            CurrentState.FreeCells.append(self.location)
            self.location = agtto
            self.location.assign(self.number)
            CurrentState.FreeCells.remove(self.location)
            return 'Move(' + move_dir_agent + ')'

        return 'NoOp'

    def Push(self, box, boxto):
        if (self.location != boxto and box.location != boxto and boxto in CurrentState.FreeCells and
                self.location not in CurrentState.FreeCells and self.color == box.color and
                box.location in CurrentState.Neighbours[self.location] and boxto in CurrentState.Neighbours[
                    box.location]):
            move_dir_agent = TranslateToDir(self.location, box.location)
            move_dir_box = TranslateToDir(box.location, boxto)
            self.location.free_cell()
            CurrentState.FreeCells.append(self.location)
            self.location = box.location
            self.location.assign(self.number)
            box.location = boxto
            box.location.assign(box.letter)
            CurrentState.FreeCells.remove(boxto)
            return 'Push(' + move_dir_agent + ',' + move_dir_box + ')'

        return 'NoOp'

    def Pull(self, agtto, box):
        if (self.location != agtto and box.location != self.location and agtto in CurrentState.FreeCells and
                box.location not in CurrentState.FreeCells and self.color == box.color and
                agtto in CurrentState.Neighbours[self.location] and self.location in CurrentState.Neighbours[
                    box.location]):
            move_dir_agent = TranslateToDir(self.location, agtto)
            curr_dir_box = TranslateToDir(self.location, box.location)
            box.location.free_cell()
            CurrentState.FreeCells.append(box.location)
            box.location = self.location
            box.location.assign(box.letter)
            self.location = agtto
            self.location.assign(self.number)
            CurrentState.FreeCells.remove(agtto)
            return 'Pull(' + move_dir_agent + ',' + curr_dir_box + ')'

        return 'NoOp'

    def ExecutePlan(self, box, cells, to_server):
        if len(cells) <= 1:
            return to_server
        cell = cells.pop(0)
        if box.location != cell:
            #ToServer(self.Move(cell))
            to_server.append(self.Move(cell))
        else:
            if cells[0] != self.location:
                #ToServer(self.Push(box, cells[0]))
                to_server.append(self.Push(box, cells[0]))
            else:
                agents_neighbours = CurrentState.Neighbours[self.location]
                small_frontier = PriorityQueue()
                goal_loc = cells[len(cells) - 1]
                for each_neighbour in agents_neighbours:
                    # this needs to be investigated for complex levels
                    small_heur = -1 * (abs(each_neighbour.x - goal_loc.x) + abs(each_neighbour.y - goal_loc.y))
                    small_frontier.put((small_heur, each_neighbour))
                while not small_frontier.empty():
                    agent_to = small_frontier.get()[1]
                    action = self.Pull(agent_to, box)
                    if action != 'NoOp':
                        #ToServer(action)
                        to_server.append(action)
                        break

        return self.ExecutePlan(box, cells, to_server)

    