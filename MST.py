from queue import PriorityQueue

def GetNextFromQueue(the_queue):
    element = the_queue.get()
    return element

#### REMEMBER TO CHANGE PATH BACK TO VERTEX AGAIN!
def MST(graph, root):
    #added for improved search
    Q_dict = dict()
    Q = PriorityQueue()
    PATH = list()
    for vertex in graph:
        if vertex==root:
            root.key = 0
            root.parent = None
            Q.put((root.key, root))
            Q_dict[vertex] = True
            continue
        vertex.key = 10000 # enough for our case, else inf
        vertex.parent = None
        Q.put((vertex.key, (vertex)))
        Q_dict[vertex] = True
    PATH.append(((root.id.x, root.id.y), (root.parent, root.parent), root.key))
    # PATH.append((root.id, root.parent, root.key))
    counter = 0
    start = len(PATH)
    while not Q.empty():
        u = Q.get()
        UUUU = u[1].id.x,u[1].id.y
        if u[1].parent != None:
            # next_in_Q = Q.get()
            # Q.put(next_in_Q)
            NOOOOOO = abs(u[1].id.x - PATH[-1][0][0]) + abs(u[1].id.y - PATH[-1][0][1])
            if abs(u[1].id.x - PATH[-1][0][0]) + abs(u[1].id.y - PATH[-1][0][1])>1:
                del PATH[start:counter+1]
                start = len(PATH)
                counter=0
            PATH.append(((u[1].id.x, u[1].id.y), (u[1].parent.id.x, u[1].parent.id.y), u[1].key))
            Q_dict[u[1]] = False
            counter+=1
            #PATH.append((u[1].id, u[1].parent.id, u[1].key))
            previous = u
        for vertex in u[1].getConnections():
            VERTEX = vertex.id.x,vertex.id.y
            if (
                # (vertex in [i[1] for i in Q.queue])
                (Q_dict[vertex] == True)
                and (u[1].getWeight(graph.getVertex(vertex.id))) < vertex.key
                ):
                oldKey = vertex.key
                vertex.key = u[1].getWeight(graph.getVertex(vertex.id))
                vertex.parent = u[1]
                # indexOfVertexInQ = Q.queue.index((oldKey, vertex))
                #is this log(n) for deletion? check if it's heapq
                #maybe don't use time on deletions as we are approaching the goal by followin min edge
                # and we empty the Q when we find one.
                # del Q.queue[indexOfVertexInQ]
                Q.put((vertex.key, vertex))
                if vertex.goal == True:
                    Q = PriorityQueue()
                    PATH.append(((vertex.id.x, vertex.id.y), (u[1].parent.id.x, u[1].parent.id.y), vertex.key))
    
    return PATH