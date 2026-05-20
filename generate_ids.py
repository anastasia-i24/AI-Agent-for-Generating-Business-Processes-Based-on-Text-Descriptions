from itertools import deque

def generate_ids(data):
    events = data['events']
    flows = data['flows']
    lanes = data['lanes']

    #first id for startEvent
    start_event = events[0]['name']
    ids = {start_event: 1}
    ID = 2
    
    #all elements except lanes will det their ids via BFS
    #creating graph using sequence_flows as edges
    graph = {}
    for f in flows:
        if f['from'] not in graph:
            graph[f['from']] = []
        graph[f['from']].append(f['to'])
        if f['to'] not in graph:
            graph[f['to']] = []
        graph[f['to']].append(f['from'])
        
    #bfs (starting from the element that goes after startEvent)
    visited = [False] * len(graph)
    visited[start_event] = True
    visited[graph[start_event][0]] = True
    queue = deque()
    queue.append(graph[start_event][0])

    while queue:
        current = queue.popleft()
        ids[current] = ID
        ID += 1
        for i in graph[current]:
            if not visited[i]:
                visited[i] = True
                queue.append(i)

    #lanes and flows get ids after that
    for i in lanes + flows:
        ids[i['name']] = ID
        ID += 1
    
    return ids