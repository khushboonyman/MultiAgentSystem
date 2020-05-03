# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 21:55:26 2020
@author :
"""


class State:
    current_level = list()
    MAX_ROW = 0
    MAX_COL = 0
    
class CurrentState:
    AgentAt = list()
    BoxAt = list()
    FreeCells = list()
    Neighbours = {}

class FinalState:
    GoalAt = list()
