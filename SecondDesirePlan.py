from plan import *
from agent import *


#agent picks goals that have no dependency and all boxes and finds shortest agent-box-goal path ..relaxed
def MakeDesirePlan(self):
    #agent prioritises request
    if len(self.request) > 0 :
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

        for letter in letters :
            if letter in State.BoxAt.keys() and letter in State.GoalAt.keys() :
                goals = State.GoalAt[letter]
                boxes = State.BoxAt[letter]
                
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
                                if goal_location not in State.GoalDependency.keys() :                        
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
                                        if ((len(plan_a_b_g) == min_plan_length and len(State.Plans[plan_b_g]) < min_b_g_length)
                                        or len(plan_a_b_g) < min_plan_length) :
                                            self.plan = plan_a_b_g.copy()
                                            self.move_box = box
                                            self.move_goal = goal_location
                                            min_plan_length = len(plan_a_b_g)
                                            min_b_g_length = len(State.Plans[plan_b_g])
        
        if self.move_box is not None :
            self.move_box.moving = True