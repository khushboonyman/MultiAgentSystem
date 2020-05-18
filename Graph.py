from state import *
import re
from location import *
from error import *
from agent import *

class Graph:
    all_vertices = set()
    def __init__(self):
        self.vertList = {}
        self.numVertices = 0

    def addVertex(self,key):
        self.numVertices = self.numVertices + 1
        newVertex = Vertex(key)
        self.vertList[key] = newVertex
        self.all_vertices.add(newVertex)
        return newVertex

    def getVertex(self, node):
        if node in self.vertList:
            return self.vertList[node]
        else:
            return None

    def __contains__(self, node):
        return node in self.vertList

    def addEdge(self,v_from,v_to,cost=0):
        if v_from not in self.vertList: 
            nv = self.addVertex(v_from)
        if v_to not in self.vertList:
            nv = self.addVertex(v_to)
        self.vertList[v_from].addNeighbor(self.vertList[v_to], cost)

    def getVertices(self):
        return self.vertList.keys()

    def __iter__(self):
        return iter(self.vertList.values())



class Vertex:
    def __init__(self,key):
        self.id = key
        self.connectedTo = {}

    def addNeighbor(self,nbr,weight=0):
        self.connectedTo[nbr] = weight

    def __str__(self):
        return str(self.id) + ' connectedTo: ' + str([x.id for x in self.connectedTo])
    
    #only added because of PQueue
    def __lt__(self, other):
        return self.key < other.key

    def getConnections(self):
        return self.connectedTo.keys()

    def getId(self):
        return self.id

    def getWeight(self,nbr):
        return self.connectedTo[nbr]


#Only solution for one goal now
def getGoal():
    pattern_box = re.compile("[A-Z]+")
    goal = State.goal_level
    for i, row in enumerate(goal):
        for j, col in enumerate(row):
            if pattern_box.fullmatch(col):
                goal_at = Location(i, j)
    return goal_at


def makeGraph():
    # State.MAX_ROW = len(State.current_level)
    # if State.MAX_ROW > limit :
    #     HandleError('Too many rows')        
    
    # State.MAX_COL = len(max(State.current_level, key=len))
    # if State.MAX_COL > limit :
    #     HandleError('Too many columns')
       
    State.Neighbours = dict() 
    State.GoalAt = dict() 
    State.Plans = dict()     
    State.AgentAt = list() 
    State.BoxAt = dict() 
    State.FreeCells = set() 
    State.GoalLocations = set()
    
    locations = list()
    pattern_agent = re.compile("[0-9]+")
    pattern_box = re.compile("[A-Z]+")
    #set up the level as a graph
    level_Graph = Graph()
    the_goal = getGoal()
    for i_index, row in enumerate(State.current_level):
        locations_of_a_row = list()
        for j_index, col in enumerate(row):
            loc = Location(i_index, j_index)
            locations_of_a_row.append(loc)
            if col == ' ' :
                level_Graph.addVertex(loc)
                State.FreeCells.add(loc)
                #MAKE MORE CLEVER TO ADD EDGES
                #ALSO! Should the edge cost be one? yes..
                for vertex in Graph.all_vertices:
                    FOOOOO = abs(loc.x - vertex.id.x) + abs(loc.y - vertex.id.y)
                    if abs(loc.x - vertex.id.x) + abs(loc.y - vertex.id.y) == 1:
                        #add the length-to-goal as edge weight.
                        len_to_goal = abs(loc.x - the_goal.x) + abs(loc.y - the_goal.y)
                        level_Graph.addEdge(vertex.id, loc, len_to_goal+1)
                        #for the reverse put +1 to the weight
                        level_Graph.addEdge(loc, vertex.id, len_to_goal)
            if pattern_agent.fullmatch(col) is not None:  #making list of agents .. list(agent)
                level_Graph.addVertex(loc)
                #MAKE MORE CLEVER TO ADD EDGES
                #ALSO! Should the edge cost be one? yes..
                for vertex in Graph.all_vertices:
                    if abs(loc.x - vertex.id.x) + abs(loc.y - vertex.id.y) == 1:
                        #add the length-to-goal as edge weight.
                        len_to_goal = abs(loc.x - the_goal.x) + abs(loc.y - the_goal.y)
                        level_Graph.addEdge(vertex.id, loc, len_to_goal+1)
                        #for the reverse put +1 to the weight
                        level_Graph.addEdge(loc, vertex.id, len_to_goal)
                for key, value in State.color_dict.items():
                    if col in value:
                        State.color_dict[key].remove(col)
                        agent = Agent(loc, key, col)
                        State.AgentAt.append(agent)
            if pattern_box.fullmatch(col) is not None:   #making dictionary og boxes .. {letter : list(box)}
                level_Graph.addVertex(loc)
                #MAKE MORE CLEVER TO ADD EDGES
                #ALSO! Should the edge cost be one? yes..
                for vertex in Graph.all_vertices:
                    FOOOOO = abs(loc.x - vertex.id.x) + abs(loc.y - vertex.id.y)
                    if abs(loc.x - vertex.id.x) + abs(loc.y - vertex.id.y) == 1:
                        #add the length-to-goal as edge weight.
                        len_to_goal = abs(loc.x - the_goal.x) + abs(loc.y - the_goal.y)
                        level_Graph.addEdge(vertex.id, loc, len_to_goal+1)
                        #for the reverse put +1 to the weight
                        level_Graph.addEdge(loc, vertex.id, len_to_goal)
                for key, value in State.color_dict.items():
                    if col in value:
                        box = Box(loc, key, col)
                        loc.box = box
                        if col not in State.BoxAt.keys() :
                            State.BoxAt[col] = list()
                        State.BoxAt[col].append(box)
            goal = State.goal_level[i_index][j_index]
            if pattern_box.fullmatch(goal) is not None:  #making dictionary of goals .. {letter : list(location)}
                for key, value in State.color_dict.items():
                    if goal in value:
                        if goal not in State.GoalAt.keys() :
                            State.GoalAt[goal] = list()    
                        State.GoalAt[goal].append(loc)
                        State.GoalLocations.add(loc)
        locations.append(locations_of_a_row)
    return level_Graph
