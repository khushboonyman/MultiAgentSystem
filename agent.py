"""
Created on Wed Apr 15 21:55:26 2020
@author :
"""

import location
from state import *
from plan import *
#import state  #contains global variables
import sys
import re
from queue import PriorityQueue
import copy

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
    def __init__(self, location, color, number, plan=[], move_box = None, move_goal = None, request = dict(), request_plan = list()):
        self.location = location
        self.color = color
        self.number = number
        self.plan = plan
        self.move_box = move_box
        self.move_goal = move_goal
        self.request = request
        self.request_plan = request_plan
        
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
        #print('from noop')
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
        #print('from move')
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

        #print('from push')
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

        print('from pull')
        return self.NoOp()

    #agent had a plan but had to execute some other tasks and now she replans because she changed location .. relaxed
    def MakeBoxGoalDesirePlan(self) :
        plan_a_b_g = list()
        plan_a_b = Plan(self.location, self.move_box.location) # Plan for the agent to reach box
        if plan_a_b in State.Plans.keys() :
            agent_has_plan_to_box = True
        else :
            agent_has_plan_to_box = plan_a_b.CreateBeliefPlan(self.location)
            if agent_has_plan_to_box :
                plan_a_b.plan.reverse()
                State.Plans[plan_a_b] = plan_a_b.plan
                    
        if agent_has_plan_to_box :
            plan_a_b_g.extend(State.Plans[plan_a_b])
            plan_b_g = Plan(self.move_box.location, self.move_goal) # Plan for the box to reach goal
            if plan_b_g in State.Plans.keys() :
                box_has_plan_to_goal = True
            else :
                box_has_plan_to_goal = plan_b_g.CreateBeliefPlan(self.move_box.location)
                if box_has_plan_to_goal :
                    plan_b_g.plan.reverse()
                    State.Plans[plan_b_g] = plan_b_g.plan
            if box_has_plan_to_goal :
                plan_a_b_g.extend(State.Plans[plan_b_g])
                self.plan = plan_a_b_g
    
    #agent has a request and needs to reach a box to free another agent .. unrelaxed
    def MakeBoxIntentionPlan(self,box) :        
        plan_a_b = Plan(self.location, box.location) # Plan for the agent to reach box        
        agent_has_plan_to_box = plan_a_b.CreateIntentionPlan(self.location,self.location)
        if agent_has_plan_to_box :
            plan_a_b.plan.reverse()
            plan_a_b.plan.pop()
            self.request_plan = plan_a_b.plan
                
    #there are some cells that are not free in the current plan, then agent tries to find another path .. unrelaxed
    def MakeCurrentIntentionPlan(self) :
        plan_a_b_g = list()
        plan_a_b = Plan(self.location, self.move_box.location) # Plan for the agent to reach box
        agent_has_plan_to_box = plan_a_b.CreateIntentionPlan(self.location,self.location)
        
        if agent_has_plan_to_box :
            plan_a_b.plan.reverse()
            plan_a_b_g.extend(plan_a_b.plan)
            plan_b_g = Plan(self.move_box.location, self.move_goal) # Plan for the box to reach goal            
            box_has_plan_to_goal = plan_b_g.CreateIntentionPlan(self.move_box.location,self.location)
            if box_has_plan_to_goal :
                plan_b_g.plan.reverse()
                plan_a_b_g.extend(plan_b_g.plan)
                self.plan = plan_a_b_g
                
    #agent picks goals that have no dependency and all boxes and finds shortest agent-box-goal path ..relaxed
    def MakeDesirePlan(self):
        #agent prioritises request
        if len(self.request) > 0 :
            return
        
        #agent had a plan but left to execute a request, so she needs to replan
        if self.move_box is not None and self.move_goal is not None :
            self.MakeBoxGoalDesirePlan()
            return
            
        letters = [letter for letter in State.color_dict[self.color]]
        min_plan_length = State.MAX_ROW*State.MAX_COL
        
        for letter in letters :
            boxes = State.BoxAt[letter]
            goals = State.GoalAt[letter]
            
            for goal_location in goals :
                #only select goals that don't have dependency
                if goal_location not in State.GoalDependency.keys() :
                    for box in boxes :  
                        plan_a_b_g = list()
                        plan_a_b = Plan(self.location, box.location) # Plan for the agent to reach box
                        #if plan was found initially
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
                            #if plan was found initially
                            if plan_b_g in State.Plans.keys() :
                                box_has_plan_to_goal = True
                            else :
                                box_has_plan_to_goal = plan_b_g.CreateBeliefPlan(box.location)
                                if box_has_plan_to_goal :
                                    plan_b_g.plan.reverse()
                                    State.Plans[plan_b_g] = plan_b_g.plan
                            if box_has_plan_to_goal :
                                plan_a_b_g.extend(State.Plans[plan_b_g])
                                #save the shortest path
                                if len(plan_a_b_g) < min_plan_length :
                                    self.plan = plan_a_b_g.copy()
                                    self.move_box = box
                                    self.move_goal = goal_location
                                    min_plan_length = len(plan_a_b_g)

    #if belief plan had no free cells and intention plan cannot be made with the chosen box-goal, find any other intention .. unrelaxed
    def MakeAnyIntentionPlan(self):
        letters = [letter for letter in State.color_dict[self.color]]
        min_plan_length = State.MAX_ROW*State.MAX_COL
        
        for letter in letters :
            boxes = State.BoxAt[letter]
            goals = State.GoalAt[letter]
            
            for goal_location in goals :
                #only choose goals that don't have dependencies
                if goal_location not in State.GoalDependency.keys() :
                    for box in boxes :  
                        plan_a_b_g = list()
                        plan_a_b = Plan(self.location, box.location) # plan for the agent to reach box                        
                        agent_has_plan_to_box = plan_a_b.CreateIntentionPlan(self.location,self.location)
                        if agent_has_plan_to_box :
                            plan_a_b.plan.reverse()
                            plan_a_b_g.extend(plan_a_b.plan)
                            plan_b_g = Plan(box.location, goal_location) # plan for the box to reach goal                            
                            box_has_plan_to_goal = plan_b_g.CreateIntentionPlan(box.location,self.location)
                            if box_has_plan_to_goal :
                                plan_b_g.plan.reverse()
                                plan_a_b_g.extend(plan_b_g.plan)
                                #pick shortest intention plan
                                if len(plan_a_b_g) < min_plan_length :
                                    self.plan = plan_a_b_g.copy()
                                    self.move_box = box
                                    self.move_goal = goal_location
                                    min_plan_length = len(plan_a_b_g)
    
    #delete box goal combinations when box is on the goal location                                
    def DeleteCells(self) :
        save_key = None
        #Delete the box that achieved goal
        State.BoxAt[self.move_box.letter].remove(self.move_box)
        if len(State.BoxAt[self.move_box.letter]) == 0 :
            del(State.BoxAt[self.move_box.letter])
        
        #Delete the goal that now has a valid box
        State.GoalAt[self.move_box.letter].remove(self.move_goal)
        if len(State.GoalAt[self.move_box.letter]) == 0 :
            del(State.GoalAt[self.move_box.letter])
        
        #Find the goals that have dependency on the goal that has been reached
        save_keys = list()
        for key,value in State.GoalDependency.items() :
            if self.move_goal in State.GoalDependency[key] :
                save_keys.append(key)
                
        #Delete the dependent goals from the dictionary and remove the key if there are no more values remaining
        for save_key in save_keys :
            State.GoalDependency[save_key].remove(self.move_goal)
            if len(State.GoalDependency[save_key]) == 0 :
                del(State.GoalDependency[save_key])
                
        self.plan = []
        self.move_box = None
        self.move_goal = None

    #if agent has received request, follow that first
    def ExecuteRequest(self) :   
        #don't pick only the first, need to improvise .. make bidding system for example
        for key,value in self.request.items() :
            other_box = key        #picking the first request
            to_free_cells = value
            break       
        
        #need to reach the box in the request
        if len(self.request_plan) == 0 :
            #only make plan to box if its not in the neighborhood
            if self.location not in State.Neighbours[other_box.location] :
                self.MakeBoxIntentionPlan(other_box)    #i chose only intentional plan for this situation
                if len(self.request_plan) > 0 : 
                    if self.request_plan[0] in State.FreeCells : 
                        return self.Move(self.request_plan.pop(0))  #agent moves towards box
                    else :
                        self.request_plan = list() #the original plan created has non free cells
                else :
                    del(self.request[other_box]) #delete request, so agent can go ahead with her own plan
                    return self.NoOp()  #agent couldn't make a plan
            else :                
                #now the agent is next to box, tries push first
                for n in State.Neighbours[other_box.location] :
                    if n in State.FreeCells and n not in to_free_cells :
                        action = self.Push(other_box,n)                        
                        if other_box in self.request.keys() :    
                            del(self.request[other_box])
                            self.plan = []                                
                        return action
                 
                #agent couldn't push, tries to pull away from the first cell that she has to free    
                agents_neighbours = State.Neighbours[self.location]
                small_frontier = PriorityQueue()
                for each_neighbour in agents_neighbours:
                    small_heur = -1 * (abs(each_neighbour.x - to_free_cells[0].x) + abs(each_neighbour.y - to_free_cells[0].y))
                    small_frontier.put((small_heur, each_neighbour))
                    while not small_frontier.empty():
                        agent_to = small_frontier.get()[1]
                        if agent_to in State.FreeCells :
                            action = self.Pull(other_box, agent_to)
                            if other_box in self.request.keys() :    
                                del(self.request[other_box])                            
                            if other_box.location in to_free_cells :
                                self.request[other_box] = to_free_cells                                 
                            return action
                
                del(self.request[other_box])  #box couldn't be moved .. blocked by another box (should make another request ?)
                                
                return self.NoOp()
        else :
            return self.Move(self.request_plan.pop(0))  #move closer to the box
                
    #make a request to some agent because the current plan cannot be executed, agent could be blocked or box could be blocked        
    def MakeRequest(self) :        
        pattern_box = re.compile("[A-Z]+")
        cell1 = self.plan[0]
        letter = State.current_level[cell1.x][cell1.y]
        if pattern_box.fullmatch(letter) is not None: 
            for box in State.BoxAt[letter] :
                if box.location == cell1 :
                    for agent in State.AgentAt :
                        if agent.color == box.color :
                            agent.request[box] = self.plan.copy()
           
    #execute the current plan
    def Execute(self):  
        #prioritise request
        if len(self.request) > 0 :
            return self.ExecuteRequest()
        
        if len(self.plan) == 0 :
            return self.NoOp()
                
        save_plan = self.plan.copy()
        
        replan = False
        for path in self.plan :
            if path not in State.FreeCells and path != self.move_box.location :
                replan = True
                break
            
        if replan :
            self.plan = list()
            self.MakeCurrentIntentionPlan()
            if len(self.plan) == 0 :
                self.MakeAnyIntentionPlan()
                if len(self.plan) == 0 :
                    self.plan = save_plan                        
        
        cell1 = self.plan[0]
        cell2 = self.plan[1]  #need to check the condition
        
        if (cell1 not in State.FreeCells and cell1 != self.move_box.location) or cell2 not in State.FreeCells  :
            self.MakeRequest()
            if len(self.request) > 0 :
                return self.ExecuteRequest()
        else :
            if self.move_box.location != cell1 :
                self.plan.pop(0)
                return self.Move(cell1)  
            else:
                if cell2 != self.location:
                    self.plan.pop(0)
                    action = self.Push(self.move_box,cell2)
                    if len(self.plan) <= 1 :
                        self.DeleteCells()   #Remove goals and boxes that have reached each other 
                    return action 
                else:
                    agents_neighbours = State.Neighbours[self.location]
                    small_frontier = PriorityQueue()
                    for each_neighbour in agents_neighbours:
                        small_heur = -1 * (abs(each_neighbour.x - self.move_goal.x) + abs(each_neighbour.y - self.move_goal.y))
                        small_frontier.put((small_heur, each_neighbour))
                    while not small_frontier.empty():
                        agent_to = small_frontier.get()[1]
                        action = self.Pull(self.move_box, agent_to)  #NEED TO CHNAGE!!!
                        if action != self.NoOp():
                            self.plan.pop(0)  
                            if len(self.plan) <= 1 :
                                self.DeleteCells()
                            return action
        return self.NoOp()
        
        
            
            
            
    