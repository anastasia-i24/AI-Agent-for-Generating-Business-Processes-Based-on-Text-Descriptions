import xml.dom.minidom as md

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
                node.appendChild(transition)
        
        if n.get('text_deco'):
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
    events = data['events']
    tasks = data['user_tasks'] + data['script_tasks']

    #изменим flows, чтобы можно было искать их названия по ключам sourceRef
    flows = {}
    for flow in data['flows']:
        flows[flow['sourceRef']] = flows.get(flow['sourceRef'], []) + [flow['name']]

    for event in events:
        #text_deco - надпись для события, если событие стартовое, подписываем сверху, иначе - снизу 
        text_deco_placement = 1 if event['id'] == 1 else -1 
        nodes.append({
            'name': f"ID{event['id']}",
            'x': str(event['x']),
            'y': str(event['y']),
            'width': '48',
            'height': '48',
            'transitions': flows.get(event['id'], []),
            'text_deco': (str(event['x']), str(event['y'] + 48 * text_deco_placement)) 
        })

    for task in tasks:
        nodes.append({
            'name': f"ID{task['id']}",
            'x': str(task['x']),
            'y': str(task['y']),
            'width': '180',
            'height': '120',
            'transitions': flows.get(task['id'], [])
        })

    return nodes