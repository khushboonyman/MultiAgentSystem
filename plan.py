# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 10:43:22 2020

@author: 
"""
from queue import PriorityQueue
from state import *
import sys
from planningClient import FindBox


def printplan(plan):
    for i in plan:
        print(i)

class Plan():
    #New states
    remove_box = set()
    parking_spot = set() # maybe a PriorityQue instead?
    parked = set()
    stopped_due_to_box = False
    box_parking_planning = False
    leaf_dictionary = dict()

    def __init__(self, start, end, color):
        self.start = start
        self.end = end
        self.frontier_set = {self.start}
        self.plan = []
        #MIGHT DELETE COLOR AGAIN
        self.color = color
        self.box_locations = [i.location for i in FindBox(self.color)] # give as parameter to save computations

    def __str__(self):
        return ('Start location  : ' + str(self.start) +
                '\nEnd location : ' + str(self.end) +
                '\nFrontier      : ' + str(self.frontier_set))

    def Heuristic(self, location):
        return abs(self.end.x - location.x) + abs(self.end.y - location.y)

    def CreatePlan(self, loc, agent_location, BOX_GOALS=set()):
        #self.end is the box.location (FOR AGENT ONLY). So when agent has reach box,
        # we can move forward and plan from box to goal. This time self.end = goal.location
        #remove_box is moved to being a class state instead
        # remove_box = list()
        if loc == self.end:
            # return (True, remove_box)
            return True
        try :
            leaves = CurrentState.Neighbours[loc]
        except Exception as ex :
            print(str(loc)+' {}'.format(repr(ex)),file=sys.stderr, flush=True)
            sys.exit(1)
            
        frontier = PriorityQueue()
        nearest_neighbour = PriorityQueue()
        nearest_neighbour_of_box = [i.location for i in FindBox(self.color)]

        #make more clever instead of rerunning for each leaf
        # i_location = [i.location for i in BOX_GOALS]

        for leaf in leaves:
            if leaf not in self.frontier_set and (leaf in CurrentState.FreeCells or leaf==self.end or leaf == agent_location):
                try:
                    #Problem can arise here, because it will only take the smallest heur and use that as plan
                    heur = self.Heuristic(leaf)
                    frontier.put((heur, leaf))
                    self.frontier_set.add(leaf)
                    nearest_neighbour.put((heur,leaf))
                    #check the logic for the if-statement below
                    #add parking spot where neighbours of leaf is not agent.location and self.end (change to below)
                    #and the parking spot must not be in the plan for the box
                    if leaf != agent_location and leaf != self.end and leaf in CurrentState.FreeCells and not self.box_parking_planning:
                        # if CurrentState.Neighbours[leaf] not
                        if leaf in BOX_GOALS:
                            heur = heur*50
                        self.parking_spot.add((heur, leaf))
                        self.leaf_dictionary[leaf] = (heur, leaf)
                    #if box.location neigbour with smallest heur contains a box of same color:
                    # move box to leaf and continue to make way
                    #maybe give as parameter to avoid recalculations
                    
                    #if location closest to goal contains a box
                    
                except Exception as ex:
                    print('error for ex ' + str(ex) + ' ' + str(heur) + ' leaf ' + str(leaf) + ' neighbours of ' + str(
                        loc))
                    while not frontier.empty():
                        h, l = frontier.get()
                        print(h, str(l))
                    sys.exit(1)
                
                #not sure about the checking of frontier. might add or delete som logic
                #(--rememember: original path with smallest heur is in frontier) unless we remove
                #if cell is free and if cell in frontier (the path) is not free:
                #   move box to free cell and clear path.
                
                #if leaf not in CurrentState and if frontier.get is next to leaf:
                # then move box to frontier.get() next to leaf
            # elif (
            #     #This should only be for box?
            #     leaf not in self.frontier_set and #Is this always the case? CHECK!
            #     leaf not in CurrentState.FreeCells #and (frontier.empty() != True)
            #     # and (frontier.get() not in CurrentState.Neighbours[leaf]) #this ensures that the neighbour is not a free cell (REDUDANT?)
            #     and (leaf in nearest_neighbour_of_box) #leaf is a box of same color. MIGHT BE USEFUL FOR CNET!
            #     and (not(any(i in CurrentState.Neighbours[leaf] for i in CurrentState.FreeCells)))# check that leaf has no free neighbours. NOT CHECKING if len()>0 because of SetupObject. Smarter way????
            #     ): # check if location is not same as agent?
            #     Plan.remove_box.add(leaf) # add location of cell where box needs to be removed.
            #     #elif leaf not in current state and if frontier.get not next to leaf or (frontier.get next to and not free) :
            #     # check if neighbours are free ...
            if (
                (leaf in self.box_locations and leaf not in self.frontier_set)
            ):
                self.stopped_due_to_box = True
            
            if (leaf in BOX_GOALS) and leaf == self.end and leaf not in CurrentState.FreeCells:
                self.stopped_due_to_box = True
                # return False MAKE SURE WHAT HAPPENS




        if frontier.empty():
            # return (False, remove_box)

            return False

        # if frontier.empty():
        #     if not(nearest_neighbour.empty()):
        #         self.plan.append(leaf) # what happens if long into the plan? will it just stick with this one single step

        #     else:
        #         return False
        else:
            while not frontier.empty():
                leaf = frontier.get()[1]
                self.stopped_due_to_box=False
                #Plan.parking_spot.append(leaf) moved to other place
                a_succesful_plan = self.CreatePlan(leaf, agent_location, BOX_GOALS)
                FOO = self.stopped_due_to_box
                if a_succesful_plan: # replace with and remove above line, self.CreatePlan(leaf, agent_location):
                    self.plan.append(leaf)
                    if leaf in self.leaf_dictionary:
                        self.parking_spot.discard(self.leaf_dictionary[leaf])
                    # return (True, remove_box)
                    return True
                elif not a_succesful_plan and self.stopped_due_to_box:
                    if leaf in self.leaf_dictionary:
                        self.parking_spot.discard(self.leaf_dictionary[leaf])
                    return False
                


            # while not frontier.empty(): #or second set not empty (second set = another way)
            #     leaf = frontier.get()[1]
            #     if self.CreatePlan(leaf, agent_location):
            #         self.plan.append(leaf)
            #         return True
