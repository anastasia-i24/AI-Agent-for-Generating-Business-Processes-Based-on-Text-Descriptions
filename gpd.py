import xml.dom.minidom as md
import networkx as nx
import ilayoutx as ilx

def gpd(path, data):
    file = md.parse(path)
    process_name = data['process_name']
    nodes = build_nodes(data)

    process_diagram = file.getElementsByTagName('process-diagram')[0]
    process_diagram.setAttribute('name', process_name)
    process_diagram.setAttribute('notation', 'bpmn')
    process_diagram.setAttribute('rendered', 'graphiti')
    process_diagram.setAttribute('showActions', 'false')
    process_diagram.setAttribute('showGrid', 'false')
    process_diagram.setAttribute('width', '1500')
    process_diagram.setAttribute('height', '1200')
    
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

                if trans['bendpoints']:
                    for b in trans['bendpoints']:
                        bendpoint = file.createElement('bendpoint')
                        bendpoint.setAttribute('x', b[0])
                        bendpoint.setAttribute('y', b[1])
                        transition.appendChild(bendpoint)

                if trans['label']:
                    label = file.createElement('label')
                    label.setAttribute('x', trans['label'][0])
                    label.setAttribute('y', trans['label'][1])
                    transition.appendChild(label)

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
    coords = get_coords(little_nodes, big_nodes)

    #изменим flows, чтобы можно было искать их названия по ключам sourceRef
    flows = {}
    for flow in data['flows']:
        flows[flow['id']] = flows.get(flow['id'], []) + [{
            'name': flow['name'],
            'bendpoints': flow.get('bendpoints'),
            'label': flow.get('label') 
        }]

    for lil in little_nodes:
        #text_deco - надпись для события, если событие стартовое, подписываем сверху, иначе - снизу 
        text_deco_placement = 1 if lil['id'] == 1 else -1
        nodes.append({
            'name': f"ID{lil['id']}",
            'x': str(coords[lil['name']][0]),
            'y': str(coords[lil['name']][1]),
            'width': '48',
            'height': '48',
            'transitions': flows.get(lil['id'], []),
            'text_deco': (coords[lil['name']][0], str(coords[lil['name']][1] + 48 * text_deco_placement)),
        })

    for biggy in big_nodes:
        nodes.append({
            'name': f"ID{biggy['id']}",
            'x': str(coords[biggy['name']][0]),
            'y': str(coords[biggy['name']][0]),
            'width': '180',
            'height': '120',
            'transitions': flows.get(biggy['id'], [])
        })

    return nodes


def get_coords(data):
    G = nx.DiGraph()

    #добавляем вершины
    vertexes = []
    little_nodes = data['events'] + data['gateways']
    big_nodes = data['user_tasks'] + data['script_tasks']
    for lil in little_nodes:
        vertexes.append((lil['name'], 48, 48))
    for biggy in big_nodes:
        vertexes.append(biggy['name'], 180, 120)
    for vertex, width, height  in vertexes:
        G.add_node(vertex, width=width, height=height)

    #добавляем ребра
    edges = [(flow['sourceRef'], flow['targetRef']) for flow in data['flows']]
    for src, dst in edges:
        G.add_edge(src, dst)

    return ilx.layouts.sugiyama(G)