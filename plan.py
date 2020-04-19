# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 10:43:22 2020

@author: Bruger
"""
from queue import PriorityQueue
from state import *

class Plan() :
    def __init__(self,start,end) :
        self.start = start
        self.end = end
        self.frontier_set = {self.start}
    
    def __str__(self) :
        return ('Start location  : ' + str(self.start)+
             '\nEnd location : '+str(self.end)+
             '\nFrontier      : '+str(self.frontier_set))
    
    def Heuristic(self,location) :
        return abs(self.end.x - location.x) + abs(self.end.y - location.y)
    
    def CreatePlan(self,loc,plan) :
        if loc == self.end :
            return plan
        
        leaves = CurrentState.Neighbours[loc]
        frontier = PriorityQueue()
        
        for leaf in leaves :
            if leaf not in self.frontier_set :
                heur = self.Heuristic(leaf)
                frontier.put((heur,leaf))
                self.frontier_set.add(leaf)
            
        if frontier.empty() :
            return list()
        else :
            while not frontier.empty() :
                leaf = frontier.get()[1]
                plan.append(leaf)
                curr_plan = self.CreatePlan(leaf,plan)
                if len(curr_plan)>0 :
                    return curr_plan
        
        return list()
        
            
            
        
        
        