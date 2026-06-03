import xml.dom.minidom as md
import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout

def gpd(path, data):
    file = md.parse(path)
    process_name = data['process_name']
    nodes, width, height = build_nodes(data)

    process_diagram = file.getElementsByTagName('process-diagram')[0]
    process_diagram.setAttribute('name', process_name)
    process_diagram.setAttribute('notation', 'bpmn')
    process_diagram.setAttribute('rendered', 'graphiti')
    process_diagram.setAttribute('showActions', 'false')
    process_diagram.setAttribute('showGrid', 'false')
    process_diagram.setAttribute('width', width)
    process_diagram.setAttribute('height', height)
    
    for n in nodes:
        node = file.createElement('node')
        node.setAttribute('name', n['name'])
        node.setAttribute('x', n['x'])
        node.setAttribute('y', n['y'])
        node.setAttribute('width', n['width'])
        node.setAttribute('height', n['height'])

        if n['transitions']:
            for trans in n['transitions']:
                transition = file.createElement('transition')
                transition.setAttribute('name', trans)
                node.appendChild(transition)
        
        if n['text_deco']:
            text_deco = file.createElement('textDecoration')
            text_deco.setAttribute('x', n['text_deco'][0])
            text_deco.setAttribute('y', n['text_deco'][1])
            text_deco.setAttribute('width', '0')
            text_deco.setAttribute('height', '0')
            node.appendChild(text_deco)

        process_diagram.appendChild(node)
    
    with open(path, 'w', encoding='utf-8') as f:
        file.writexml(f, indent='', addindent='  ', newl='\n', encoding='utf-8')


def build_nodes(data):
    nodes = []
    little_nodes = data['events'] + data['gateways'] # 48 x 48
    big_nodes = data['user_tasks'] + data['script_tasks'] # 180 x 120
    coords, width, height = get_coords(little_nodes + big_nodes, data['flows'])

    #изменим flows, чтобы можно было искать их названия по ключам sourceRef
    flows = {}
    for flow in data['flows']:
        flows.setdefault(flow['sourceRef'], []).append(flow['name'])
    

    for lil in little_nodes:
        #text_deco - надпись для события, если событие стартовое, подписываем сверху, иначе - снизу 
        text_deco_placement = 1 if lil['id'] == 1 else -1
        nodes.append({
            'name': f"ID{lil['id']}",
            'x': str(int(coords[lil['id']][0])),
            'y': str(int(coords[lil['id']][1])),
            'width': '48',
            'height': '48',
            'transitions': flows.get(lil['id']),
            'text_deco': (str(int(coords[lil['id']][0])), str(int(coords[lil['id']][1]) + 48 * text_deco_placement))
        })

    for biggy in big_nodes:
        nodes.append({
            'name': f"ID{biggy['id']}",
            'x': str(int(coords[biggy['id']][0])),
            'y': str(int(coords[biggy['id']][1])),
            'width': '180',
            'height': '120',
            'transitions': flows.get(biggy['id']),
            'text_deco': None
        })

    return nodes, width, height


def get_coords(nodes, flows):
    G = nx.DiGraph()

    # добавляем вершины
    for node in nodes:
        G.add_node(node['id'], label=node['name'])

    # добавляем рёбра
    for flow in flows:
        G.add_edge(flow['sourceRef'], flow['targetRef'])
    
    pos = graphviz_layout(G, prog='dot')

    # масштабируем 
    all_x = [p[0] for p in pos.values()]
    all_y = [p[1] for p in pos.values()]
    
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    range_x = max_x - min_x if max_x - min_x != 0 else 1
    range_y = max_y - min_y if max_y - min_y != 0 else 1
    
    scale = max(800, len(nodes) * 100)
    
    margin = 50
    target_width = scale
    target_height = int(scale * (range_y / range_x)) if range_x > 0 else scale
    
    coords = {}
    for i, (x, y) in pos.items():
        nx_norm = (x - min_x) / range_x
        ny_norm = (y - min_y) / range_y
        
        screen_x = margin + nx_norm * (target_width - 2 * margin)
        screen_y = margin + ny_norm * (target_height - 2 * margin)
        
        coords[i] = (int(screen_x), int(screen_y))
    
    return coords, str(target_width), str(target_height)