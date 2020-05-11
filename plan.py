# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 10:43:22 2020

@author: 
"""
from queue import PriorityQueue
from state import *
import sys


def printplan(plan):
    for i in plan:
        print(i)

class Plan():
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.frontier_set = {self.start}
        self.plan = []
        self.blocked_by_box = None

    def __str__(self):
        return ('Start location  : ' + str(self.start) +
                '\nEnd location : ' + str(self.end) +
                '\nFrontier      : ' + str(self.frontier_set))

    def Heuristic(self, location):
        return abs(self.end.x - location.x) + abs(self.end.y - location.y)

    def CreatePlan(self, loc, agent_location):
        if loc == self.end:
            return True        
        try :
            leaves = CurrentState.Neighbours[loc]
        except Exception as ex :
            print(str(loc)+' {}'.format(repr(ex)),file=sys.stderr, flush=True)
            sys.exit(1)
            
        frontier = PriorityQueue()

        for leaf in leaves:
            if leaf not in self.frontier_set and (leaf in CurrentState.FreeCells or leaf==self.end or leaf == agent_location) :
                try:
                    heur = self.Heuristic(leaf)
                    frontier.put((heur, leaf))
                    self.frontier_set.add(leaf)
                except Exception as ex:
                    print('error for ex ' + str(ex) + ' ' + str(heur) + ' leaf ' + str(leaf) + ' neighbours of ' + str(
                        loc))
                    while not frontier.empty():
                        h, l = frontier.get()
                        print(h, str(l))
                    sys.exit(1)
            else:
                for box in CurrentState.BoxAt:
                    if box.location == leaf:
                        self.blocked_by_box = box

        if frontier.empty():
            return False
        else:
            while not frontier.empty():
                leaf = frontier.get()[1]
                if self.CreatePlan(leaf, agent_location):
                    self.plan.append(leaf)
                    return True
