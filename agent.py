"""
Created on Wed Apr 15 21:55:26 2020
@author :
"""

import location
from box import Box
from state import *
from plan import *
#import state  #contains global variables
import sys
import re
from queue import PriorityQueue
import copy
from collections import deque

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
    def __init__(self, location, color, number, plan=[], move_box = None, move_goal = None, request_plan = list(), box_paths = dict()):
        self.location = location
        self.color = color
        self.number = number
        self.plan = plan
        self.move_box = move_box
        self.move_goal = move_goal
        self.request = dict()
        self.request_plan = request_plan
        self.box_paths = box_paths

        self.pending_goals = []
        
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

    #agent had a plan but had to execute some other tasks and now she replans because she changed location .. relaxed
    def MakeBoxGoalDesirePlan(self) :
        plan_a_b_g = deque()
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
        plan_a_b_g = deque()
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
        if len(self.request) > 0 :   #should at least plan
            return

        #agent had a plan but left to execute a request, so she needs to replan
        if self.move_box is not None and self.move_goal is not None :
            self.MakeBoxGoalDesirePlan()
            return

        letters = []
        if self.color in State.color_dict.keys():
            letters = [letter for letter in State.color_dict[self.color]]
            min_plan_length = State.MAX_ROW*State.MAX_COL
            min_b_g_length = State.MAX_ROW*State.MAX_COL

            prime_goals = []
            second_goals = []
            for letter, location in State.GoalAt.items():
                for l in location:
                    if len(State.Neighbours[l]) == 1:
                        prime_goals.append(letter)
                    elif len(State.Neighbours[l]) == 2:
                        second_goals.append(letter)

            prime_goals.extend(second_goals)
            prime_goal_counter = 0
            goal_sequence = []

            if prime_goals:
                goal_sequence = [prime_goals[prime_goal_counter]]
            else:
                goal_sequence = letters
            #goal_sequence_locations = []
            #box_sequence = []

            letter_list = []
            if self.pending_goals:
                letter_list = self.pending_goals
            else:
                letter_list = goal_sequence


            for letter in letter_list :
                if letter in State.BoxAt.keys() and letter in State.GoalAt.keys() :
                    goals = State.GoalAt[letter]
                    boxes = State.BoxAt[letter]


                    print('TOTAL: {}'.format(letter_list), file=sys.stderr, flush=True)
                    for box in boxes :
                        if not box.moving :

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

                                plan_a_b_g = State.Plans[plan_a_b].copy()
                                for goal_location in goals :
                                    #only select goals that don't have dependency
                                    #if goal_location not in State.GoalDependency.keys() :  
                                    if True:   

                                        #print('FIRST: {}'.format(box), file=sys.stderr, flush=True)

                                        plan_b_g = Plan(box.location, goal_location) # Plan for the box to reach goal
                                        #if plan was found initially
                                        if plan_b_g in State.Plans.keys() :
                                            box_has_plan_to_goal = True
                                        else :
                                            box_has_plan_to_goal = plan_b_g.CreateBeliefPlan(box.location)
                                            if box_has_plan_to_goal :
                                                plan_b_g.plan.reverse()
                                                State.Plans[plan_b_g] = plan_b_g.plan

                                                if not self.pending_goals:
                                                    encount_goals = []
                                                    for cell in list(State.Plans[plan_b_g])[:-1]:
                                                        if cell in State.GoalLocations:
                                                            encount_goals.append(State.goal_level[cell.x] [cell.y])

                                                    if encount_goals and goal_sequence:
                                                        encount_goals.reverse()
                                                        goal_sequence.extend(encount_goals)

                                                    if prime_goal_counter < len(prime_goals) - 1:
                                                        prime_goal_counter += 1
                                                        goal_sequence.append(prime_goals[prime_goal_counter])

                                                    self.pending_goals.extend(encount_goals)
                                                else:
                                                    self.pending_goals.pop(0)

                                        if box_has_plan_to_goal :
                                            plan_a_b_g.extend(State.Plans[plan_b_g])
                                            #save the shortest path
                                            #if ((len(plan_a_b_g) == min_plan_length and len(State.Plans[plan_b_g]) < min_b_g_length)
                                            #or len(plan_a_b_g) < min_plan_length) :

                                            #print('SECOND: {}'.format(box), file=sys.stderr, flush=True)

                                            self.plan = plan_a_b_g.copy()
                                            self.move_box = box
                                            self.move_goal = goal_location
                                            min_plan_length = len(plan_a_b_g)
                                            min_b_g_length = len(State.Plans[plan_b_g])
                break
            
            if self.move_box is not None :
                self.move_box.moving = True

            #print('\n', file=sys.stderr, flush=True)

    #if belief plan had no free cells and intention plan cannot be made with the chosen box-goal, find any other intention .. unrelaxed
    def MakeAnyIntentionPlan(self):
        letters = [letter for letter in State.color_dict[self.color]]
        min_plan_length = State.MAX_ROW*State.MAX_COL
        min_b_g_length = State.MAX_ROW*State.MAX_COL
        
        for letter in letters :
            if letter in State.BoxAt.keys() and letter in State.GoalAt.keys() :                
                boxes = State.BoxAt[letter]
                goals = State.GoalAt[letter]
                
                for goal_location in goals :
                    #only choose goals that don't have dependencies
                    if goal_location not in State.GoalDependency.keys() :
                        for box in boxes :  
                            if not box.moving :                               
                                plan_a_b_g = deque()
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
                                        if ((len(plan_a_b_g) == min_plan_length and len(plan_b_g.plan) < min_b_g_length)
                                        or len(plan_a_b_g) < min_plan_length) :
                                            self.plan = plan_a_b_g.copy()
                                            self.move_box = box
                                            self.move_goal = goal_location
                                            min_plan_length = len(plan_a_b_g)
                                            min_b_g_length = len(plan_b_g.plan)
        if self.move_box is not None :
            self.move_box.moving = True
                                
    def DeleteRequest(self,key) :
        try :
            del(self.request[key])
        except Exception as ex :
            HandleError("delete error "+str(key)+' '+str(self)+' '+str(self.move_box))
            
    #delete box goal combinations when box is on the goal location                                
    def DeleteCells(self) :
        save_key = None
        
        #Delete the box that achieved goal
        State.BoxAt[self.move_box.letter].remove(self.move_box)
        if len(State.BoxAt[self.move_box.letter]) == 0 :
            del(State.BoxAt[self.move_box.letter])
            State.color_dict[self.color].remove(self.move_box.letter)
            if len(State.color_dict[self.color]) == 0 :
                del(State.color_dict[self.color])
        
        #Delete the goal that now has a valid box        
        State.GoalAt[self.move_box.letter].remove(self.move_goal)
        if len(State.GoalAt[self.move_box.letter]) == 0 :
            del(State.GoalAt[self.move_box.letter])
        
        #Find the goals that have dependency on the goal that has been reached
        save_keys = deque()
        for key,value in State.GoalDependency.items() :
            if self.move_goal in State.GoalDependency[key] :
                save_keys.append(key)
                
        #Delete the dependent goals from the dictionary and remove the key if there are no more values remaining
        while len(save_keys) != 0 :
            save_key = save_keys.pop() 
            State.GoalDependency[save_key].remove(self.move_goal)
            if len(State.GoalDependency[save_key]) == 0 :
                del(State.GoalDependency[save_key])
                
        self.plan = deque()
        self.move_box = None
        self.move_goal = None

    def MoveOtherBox(self,other_box,to_free_cells) :
        #need to reach the box in the request
        if len(self.request_plan) > 0 :
            return self.Move(self.request_plan.popleft())  #move closer to the box
        #only make plan to box if its not in the neighborhood
        
        if self.location not in State.Neighbours[other_box.location] :
            
            self.MakeBoxIntentionPlan(other_box)    #i chose only intentional plan for this situation
            if len(self.request_plan) > 0 :
                move_cell = self.request_plan.popleft()
                if  move_cell in State.FreeCells :
                    self.plan = deque()
                    return self.Move(move_cell)  #agent moves towards box
                else :
                    self.request_plan = deque() #the original plan created has non free cells
            else :
                self.DeleteRequest(other_box) #delete request, so agent can go ahead with her own plan
                return self.NoOp()  #agent couldn't make a plan
        
        else :
            #now the agent is next to box, tries push first
            push_cells = deque()
            for n in State.Neighbours[other_box.location] :
                if n in State.FreeCells :
                    if n not in to_free_cells :
                        self.DeleteRequest(other_box)
                        action = self.Push(other_box,n)
                        self.plan = deque()
                        return action
                    else :
                        push_cells.append(n)

            #agent couldn't push, tries to pull away from the first cell that she has to free
            pull_cells = deque()
            for n in State.Neighbours[self.location]:
                if n in State.FreeCells :
                    if n not in to_free_cells :
                        self.DeleteRequest(other_box)
                        action = self.Pull(other_box, n)
                        self.plan = deque()
                        return action
                    else :
                        pull_cells.append(n)

            if len(pull_cells) > 0 or len(push_cells) > 0 :
                self.plan = deque()
                self.DeleteRequest(other_box)
                if len(pull_cells) > 0 :
                    cell = pull_cells.popleft()
                    action = self.Pull(other_box, cell) #pull to any neighbour
                else :
                    cell = push_cells.popleft()
                    action = self.Push(other_box, cell) #push to any neighbour
                self.request[other_box] = to_free_cells
                return action
            else :
                self.DeleteRequest(other_box)  #box couldn't be moved .. blocked by another box (should make another request ?)

            return self.NoOp()
        
    def MoveAnotherPlace(self,to_free_cells) :
        action = self.NoOp()
        for n in State.Neighbours[self.location]:
            if n in State.FreeCells and n not in to_free_cells:
                action = self.Move(n)
                break
        self.DeleteRequest(1)
        if self.location in to_free_cells:
            self.request[1] = to_free_cells
        return action
        
    #if agent has received request, follow that first
    def ExecuteRequest(self) :
        #don't pick only the first, need to improvise .. make bidding system for example
        for key in self.request.keys():
            blocking_entity = key  # picking the first request
            to_free_cells = set()
            break

        for value in self.request.values():
            to_free_cells.update(value)

        if type(blocking_entity) is int :
            return self.MoveAnotherPlace(to_free_cells)
        else:
            return self.MoveOtherBox(blocking_entity,to_free_cells)
            
                
    #make a request to some agent because the current plan cannot be executed, agent could be blocked or box could be blocked        
    def MakeRequest(self,free_these_cells) :        
        pattern_box = re.compile("[A-Z]+")
        pattern_agent = re.compile("[0-9]+")

        for cell in free_these_cells :
            letter_or_num = State.current_level[cell.x][cell.y]
            if pattern_box.fullmatch(letter_or_num) is not None:
                if letter_or_num in State.BoxAt.keys() :                    
                    for box in State.BoxAt[letter_or_num] :
                        if box.location == cell :
                            if not box.moving :                                
                                for agent in State.AgentAt :
                                    if agent.color == box.color :
                                        agent.request[box] = set(self.plan)
                                        break
            elif pattern_agent.fullmatch(letter_or_num) is not None:
                agent = State.getAgent(letter_or_num)
                if len(agent.plan) == 0:
                    agent.request[1] = set(self.plan)
        
    def ExecuteDecision(self) :
        
        cell1 = self.plan.popleft()
        cell2 = self.plan[0]  

        #print('EXECUTE: {}'.format(self.move_box), file=sys.stderr, flush=True)
        
        #Move towards the box
        if self.move_box.location != cell1 :
            return self.Move(cell1)  
        else:
            #If next to next location is where box should be, then push
            if cell2 != self.location :
                action = self.Push(self.move_box,cell2)
                if len(self.plan) <= 1 :
                    self.DeleteCells()   #Remove goals and boxes that have reached each other 
                return action 
            else:
                #if next to next location is agent's location, then pull
                small_frontier = PriorityQueue()
                for n in State.Neighbours[self.location]:
                    if n in State.FreeCells and n != self.move_box.location :
                        small_heur = -1 * (abs(n.x - self.move_goal.x) + abs(n.y - self.move_goal.y))
                        small_frontier.put((small_heur, n))
                if not small_frontier.empty():
                    agent_to = small_frontier.get()[1]
                    action = self.Pull(self.move_box, agent_to)                            
                    if len(self.plan) <= 1 :
                        self.DeleteCells()
                    return action
                return self.NoOp()
        
    #check for requests, check for feasibility of the plan and execute 
    def CheckAndExecute(self):  

        #prioritise request
        if len(self.request) > 0 :
            return self.ExecuteRequest()
        
        #if no desire plan was made, then agent doesn't have more plans
        if len(self.plan) == 0 :
            return self.NoOp()
                
        #save the desire plan
        save_plan = self.plan.copy()   
        
        replan = False
        
        #find if any desire plan path is not free
        not_free_cells = set(self.plan).difference(State.FreeCells)
        not_free_cells.discard(self.move_box.location)
        not_free_cells.discard(self.location)
        
        if len(not_free_cells) != 0 :
            replan = True
        
        #while replanning, make intentional plan
        if replan :
            #print('REPLANNING: {}'.format(self.move_box), file=sys.stderr, flush=True)
            self.plan = deque()
            self.move_box.moving = False
            #first try with chosen box and goal
            self.MakeCurrentIntentionPlan()
            if len(self.plan) == 0 :
                #if cannot make plan with chosen box and goal, then chose any plan that can be achieved
                self.MakeAnyIntentionPlan()
                if len(self.plan) == 0 : #if no plan could be made, keep the original plan 
                    self.plan = save_plan
                    self.move_box.moving = True
                    self.MakeRequest(not_free_cells) #make request to agent whose box blocks the current agent
                    if len(self.request) > 0 :  #if request was made to self, then execute
                        return self.ExecuteRequest()
                    else :
                        return self.NoOp()

        #print(self.move_box, file=sys.stderr, flush=True)
        if len(self.plan) > 1 :
            return self.ExecuteDecision()
        else :
            self.plan = deque()
            return self.NoOp()