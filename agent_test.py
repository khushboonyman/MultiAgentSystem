# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 11:37:17 2020

@author: Bruger
"""

loc00 = Location(0,0)
loc01 = Location(0,1)
loc02 = Location(0,2)
loc10 = Location(1,0)
loc11 = Location(1,1)
loc12 = Location(1,2)
loc20 = Location(2,0)
loc21 = Location(2,1)
loc22 = Location(2,2)

State.current_state=['   ']*3

agent_0 = Agent(loc11,'red','0')

box_A = Box(loc01,'red','A')

print(agent_0.Push(box_A,loc00))
print(agent_0.Pull(loc02,box_A))
print(agent_0.Move(loc12))


for i in State.current_state :
    print(i)
