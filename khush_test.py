# -*- coding: utf-8 -*-
"""
Created on Mon May 11 14:40:32 2020

@author: Bruger
"""

for p in State.Plans :
    print(p)
    for i in p.plan :
        print(i)
        

for key,value in State.GoalDependency.items() :
    print(key)
    print('is dependent on')
    for v in value :
        print(v)
    print()

########################TESTING##################################

    
   

       
                        