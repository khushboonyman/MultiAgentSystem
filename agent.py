"""
Created on Wed Apr 15 21:55:26 2020
@author :
"""

import location
from state import *
from plan import *
#import state  #contains global variables
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
    def __init__(self, location, color, number, plan=[], move_box = None, move_goal = None, request = list()):
        self.location = location
        self.color = color
        self.number = number
<<<<<<< HEAD
        self.plan = plan
        self.move_box = move_box
        self.move_goal = move_goal
        self.request = request
        
=======
        self.conflicts = False
        self.blocked_by_box = False

>>>>>>> 372dc30b33f63ffec7716b8b437d40638b8474ea
    def __str__(self):
        return str(self.location) + ' Color : ' + self.color + ' Letter : ' + self.number

    def __hash__(self):
        return hash(self.number)
    
    def __eq__(self, other):
        if self.number == other.number :
            return True
        return False
    
    def __ne__(self, other):
        if self.number != other.number :
            return True
        return False
    
    def __lt__(self, other):
        if self.number < other.number :
            return True
        return False
    
    def __gt__(self, other):
        if self.number > other.number :
            return True
        return False
    
    def NoOp(self) :
        return 'NoOp'
    
    def Move(self, agtto):
        if (self.location != agtto and agtto in State.FreeCells and agtto in State.Neighbours[self.location]):
            move_dir_agent = TranslateToDir(self.location, agtto)
            self.location.free_cell()
            State.FreeCells.add(self.location)
            self.location = agtto
            self.location.assign(self.number)
            State.FreeCells.remove(self.location)
            return 'Move(' + move_dir_agent + ')'
        return self.NoOp()

    def Push(self, box, boxto):
        if (self.location != boxto and box.location != boxto and boxto in State.FreeCells and self.color == box.color 
        and box.location in State.Neighbours[self.location] and boxto in State.Neighbours[box.location]):
            move_dir_agent = TranslateToDir(self.location, box.location)
            move_dir_box = TranslateToDir(box.location, boxto)
            self.location.free_cell()
            State.FreeCells.add(self.location)
            self.location = box.location
            self.location.assign(self.number)
            box.location = boxto
            box.location.assign(box.letter)
            State.FreeCells.remove(boxto)
            return 'Push(' + move_dir_agent + ',' + move_dir_box + ')'

        return self.NoOp()

    def Pull(self, box, agtto):
        if (self.location != agtto and box.location != self.location and agtto in State.FreeCells and self.color == box.color
        and agtto in State.Neighbours[self.location] and self.location in State.Neighbours[box.location]):
            move_dir_agent = TranslateToDir(self.location, agtto)
            curr_dir_box = TranslateToDir(self.location, box.location)
            box.location.free_cell()
            State.FreeCells.add(box.location)
            box.location = self.location
            box.location.assign(box.letter)
            self.location = agtto
            self.location.assign(self.number)
            State.FreeCells.remove(agtto)
            return 'Pull(' + move_dir_agent + ',' + curr_dir_box + ')'

        return self.NoOp()

    def MakePlan(self):
        if len(self.request) > 0 :
            return
        letters = [letter for letter in State.color_dict[self.color]]
        min_plan_length = State.MAX_ROW*State.MAX_COL
        min_b_g_length = State.MAX_ROW*State.MAX_COL
        for letter in letters :
            boxes = State.BoxAt[letter]
            goals = State.GoalAt[letter]
            
            for goal_location in goals :
                if goal_location in State.GoalLocations and goal_location not in State.GoalDependency.keys() :
                    for box in boxes :  
                        plan_a_b_g = list()
                        plan_a_b = Plan(self.location, box.location) # Plan for the agent to reach box
                        if plan_a_b in State.Plans.keys() :
                            agent_has_plan_to_box = True
                        else :
                            agent_has_plan_to_box = plan_a_b.CreateBeliefPlan(self.location)
                            if agent_has_plan_to_box :
                                plan_a_b.plan.reverse()
                                State.Plans[plan_a_b] = plan_a_b.plan
                    
                        if agent_has_plan_to_box :
                            plan_a_b_g.extend(State.Plans[plan_a_b])
                            plan_b_g = Plan(box.location, goal_location) # Plan for the box to reach goal
                            if plan_b_g in State.Plans.keys() :
                                box_has_plan_to_goal = True
                            else :
                                box_has_plan_to_goal = plan_b_g.CreateBeliefPlan(box.location)
                                if box_has_plan_to_goal :
                                    plan_b_g.plan.reverse()
                                    State.Plans[plan_b_g] = plan_b_g.plan
                            if box_has_plan_to_goal :
                                plan_a_b_g.extend(State.Plans[plan_b_g])
                                if (len(plan_a_b_g) < min_plan_length 
                                or len(plan_a_b_g) == min_plan_length and len(plan_b_g.plan) < min_b_g_length) :
                                    self.plan = plan_a_b_g.copy()
                                    self.move_box = box
                                    self.move_goal = goal_location
                                    min_plan_length = len(plan_a_b_g)
                                    min_b_g_length = len(plan_b_g.plan)

    def DeleteCells(self) :
        save_key = None
        State.BoxAt[self.move_box.letter].remove(self.move_box)
        if len(State.BoxAt[self.move_box.letter]) == 0 :
            del(State.BoxAt[self.move_box.letter])
        
        State.GoalAt[self.move_box.letter].remove(self.move_goal)
        if len(State.GoalAt[self.move_box.letter]) == 0 :
            del(State.GoalAt[self.move_box.letter])
            
        State.GoalLocations.remove(self.move_goal)
        for key,value in State.GoalDependency.items() :
            if self.move_goal in State.GoalDependency[key] :
                save_key = key
                break
        if save_key is not None :
            State.GoalDependency[save_key].remove(self.move_goal)
            if len(State.GoalDependency[save_key]) == 0 :
                del(State.GoalDependency[save_key])
            self.plan = []
            self.move_box = None
            self.move_goal = None

    def ExecuteRequest(self) :
        action = 'NoOp'
        
        if len(self.request) == 2 :
            other_box = self.request[0]
            to_free_cells = self.request[1]
            for n in State.Neighbours[other_box.location] :
                if n in State.FreeCells and n not in to_free_cells :
                    action = self.Push(other_box,n)
                    self.request = list()
                    return action
                
            agents_neighbours = State.Neighbours[self.location]
            small_frontier = PriorityQueue()
            for each_neighbour in agents_neighbours:
                small_heur = -1 * (abs(each_neighbour.x - to_free_cells[0].x) + abs(each_neighbour.y - to_free_cells[0].y))
                small_frontier.put((small_heur, each_neighbour))
                while not small_frontier.empty():
                    agent_to = small_frontier.get()[1]
                    action = self.Pull(other_box, agent_to)
                    if action != self.NoOp():
                        self.request = list()
                        return action
        else :
            to_free_cells = self.request[0]
            for n in State.Neighbours[self.location] :
                if n in State.FreeCells and n not in to_free_cells :
                    self.request = list()
                    action = self.Move(n)
                        
        return action
                        
    def MakeRequest(self) :        
        if len(self.request) == 0 :
            cell1 = self.plan[0]
            letter = State.current_level[cell1.x][cell1.y]
            req = list()
            for box in State.BoxAt[letter] :
                if box.location == cell1 :
                    req = [box,self.plan]
                    break
            if len(req) == 0 :
                for agent in State.AgentAt :
                    if agent.location == cell1 :
                        agent.request = [self.plan]
            else :
                for agent in State.AgentAt :
                    if agent.color == box.color :
                        agent.request = req 
        
        self.plan = list()
        self.move_box = None
        self.move_goal = None
           
    def Execute(self):   
        if len(self.request) > 0 :
            return self.ExecuteRequest()
        #check for free cells
        if len(self.plan) == 0 :
            self.MakePlan()
        
        if len(self.plan) == 0 :
            return self.NoOp()
        
        cell1 = self.plan[0]
                
        if self.move_box.location != cell1 :
            if cell1 in State.FreeCells :
                self.plan.pop(0)
                return self.Move(cell1)  
            else :
                self.MakeRequest()
                if len(self.request) > 0 :
                    return self.ExecuteRequest() 
        else:
            cell2 = self.plan[1]
            #Remove goals and boxes that have reached each other         
                
            if cell2 != self.location:
                if cell2 in State.FreeCells :
                    self.plan.pop(0)
                    action = self.Push(self.move_box,cell2)
                    if len(self.plan) == 1 :
                        self.DeleteCells()
                    return action 
                else :
                    self.MakeRequest()
                    if len(self.request) > 0 :
                        return self.ExecuteRequest() 
            else:
                agents_neighbours = State.Neighbours[self.location]
                small_frontier = PriorityQueue()
                for each_neighbour in agents_neighbours:
                    small_heur = -1 * (abs(each_neighbour.x - self.move_goal.x) + abs(each_neighbour.y - self.move_goal.y))
                    small_frontier.put((small_heur, each_neighbour))
                while not small_frontier.empty():
                    agent_to = small_frontier.get()[1]
                    action = self.Pull(self.move_box, agent_to)
                    if action != self.NoOp():
                        self.plan.pop(0)  
                        if len(self.plan) == 1 :
                            self.DeleteCells()
                        return action
                return self.NoOp()
        return self.NoOp()
        
        
            
            
            
    