# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 10:43:22 2020

@author: 
"""
from queue import PriorityQueue
from state import *
import sys
from error import *
from collections import deque
    
class Plan():
    #maybe move down under init???
    remove_box = set()
    parking_spot = set() # maybe a PriorityQue instead?
    parked = dict() #changed from set
    stopped_due_to_box = False
    box_parking_planning = False
    planning_to_goal = False
    leaf_dictionary = dict()
    BANNED_parking_spot = dict()
    LAST_parking_spot = set()
    IN_GOAL = dict()
    STILL_PARKING = dict()
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.frontier_set = {self.start}
        self.plan = deque()


    def __eq__(self,other) :
        if self.start == other.start and self.end == other.end :
            return True
        return False
    
    def __hash__(self) :
        return hash(str(self))
    
    def __str__(self):
        return ('Start : ' + str(self.start) +' End : ' + str(self.end))

    def Heuristic(self, location): #we need to improve the heuristic
        return abs(self.end.x - location.x) + abs(self.end.y - location.y)

    #while finding a plan, relax the preconditions .. make A* instead .. 
    def CreateBeliefPlan(self, loc):
        if loc == self.end :
            return True        
        try :
            leaves = State.Neighbours[loc]
        except Exception as ex :
            HandleError('Plan'+str(loc)+' '+repr(ex))
            
        frontier = PriorityQueue()

        for leaf in leaves:
            if leaf not in self.frontier_set :
                try:
                    heur = self.Heuristic(leaf)
                    frontier.put((heur, leaf))
                    self.frontier_set.add(leaf)
                except Exception as ex:
                    HandleError('Plan'+str(ex) + ' ' + str(heur) + ' leaf ' + str(leaf) + ' neighbours of ' + str(loc))

        if frontier.empty():
            return False
        else:
            while not frontier.empty():
                leaf = frontier.get()[1]
                if self.CreateBeliefPlan(leaf):
                    self.plan.append(leaf)
                    State.Paths.add(leaf)
                    return True

    
    def findCells(self, choice):
        locations = set()
        locations_dict=dict()
        if choice == 1:
            for key, value in State.BoxAt.items():
                locations.add(value[0].location)
            return locations
        elif choice == 2:
            for key, value in State.GoalAt.items():
                locations.add(value[0])
            return locations
        elif choice == 3:
            for key, value in State.GoalAt.items():
                locations_dict[value[0]] = key
            return locations_dict


    #while finding a plan, take preconditions into account
    def CreateIntentionPlan(self, loc, agent_location, BOX_GOALS=set()):
        if loc == self.end:
            box_at_other_box_goal = False
            a = bool(self.STILL_PARKING)
            for key,value in self.parked.items():
                #if self.end == value[1]:
                if (value[1].__eq__(self.end)) and not self.box_parking_planning:
                    box_at_other_box_goal = True
            # if len(self.STILL_PARKING)>0 and self.end in self.STILL_PARKING.values():
            #     box_at_other_box_goal = True
            if not box_at_other_box_goal:
                # return (True, remove_box)
                return True
        try :
            leaves = State.Neighbours[loc]
        except Exception as ex :
            HandleError('Plan '+str(loc)+' '+repr(ex))
            
        frontier = PriorityQueue()
        box_locations = self.findCells(1)
        BOX_GOALS = self.findCells(2)
        GOALS_BOX = self.findCells(3)

        for leaf in leaves:
            if leaf not in self.frontier_set and (leaf in State.FreeCells or leaf==self.end or leaf == agent_location) :
                try:
                    heur = self.Heuristic(leaf)
                    frontier.put((heur, leaf))
                    self.frontier_set.add(leaf)
                    if (leaf != agent_location and leaf != self.end and leaf in State.FreeCells and not self.box_parking_planning
                        and leaf not in self.IN_GOAL):
                        # if leaf in BOX_GOALS:
                        #     heur = heur+2                        
                        # if CurrentState.Neighbours[leaf] not
                        #create heuristic based on parking spot from box location.
                        #find leaf in box_goals. If the leaf is in parking spot, then assign it +1 (maybe +the prev parkingspot)
                        dist_from_box = abs(leaf.x - Plan.box_being_moved.x) + abs(leaf.y - Plan.box_being_moved.y)
                        if leaf in GOALS_BOX:
                            a = GOALS_BOX[leaf]
                            if a in Plan.parked and leaf == State.GoalAt[a][0]:# Plan.parked[a][1]:
                                dist_from_box +=1
                        #MAKE SURE THAT IF IT's NoOp, then try with another parking spot
                        # I.e. ban that parking spot for the specific box.
                        self.parking_spot.add((dist_from_box, leaf))
                        self.leaf_dictionary[leaf] = (dist_from_box, leaf) 
                        # self.leaf_dictionary[leaf] = (heur, leaf)                    
                except Exception as ex:
                    HandleError('Plan'+str(ex) + ' ' + str(heur) + ' leaf ' + str(leaf) + ' neighbours of ' + str(loc))
            if (
                (leaf in box_locations and leaf not in self.frontier_set)
            ):
                self.stopped_due_to_box = True
            if (leaf in BOX_GOALS) and leaf == self.end and leaf not in State.FreeCells:
                self.stopped_due_to_box = True
                # return False MAKE SURE WHAT HAPPENS
            if (leaf not in BOX_GOALS) and leaf == self.end and leaf in State.FreeCells:
                self.stopped_due_to_box = False

        if frontier.empty():
            return False
        else:
            while not frontier.empty():
                leaf = frontier.get()[1]
                # self.stopped_due_to_box=False
                a_succesful_plan = self.CreateIntentionPlan(leaf, agent_location, BOX_GOALS)
                FOO = self.stopped_due_to_box
                if a_succesful_plan:
                    self.plan.append(leaf)
                    if leaf in self.leaf_dictionary:
                        self.parking_spot.discard(self.leaf_dictionary[leaf])
                    return True
                elif not a_succesful_plan and self.stopped_due_to_box:
                    if leaf in self.leaf_dictionary:
                        self.parking_spot.discard(self.leaf_dictionary[leaf])
                    return False
                
    


