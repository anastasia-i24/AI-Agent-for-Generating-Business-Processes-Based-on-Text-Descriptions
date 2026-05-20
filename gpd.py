import xml.dom.minidom as md

def gpd(path, data, ids):
    file = md.parse(path)
    process_name = data['process_name']
    nodes = build_nodes(data, ids)

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


def build_nodes(data, ids):
    nodes = []
    little_nodes = data['events'] + data['gateways'] # 48 x 48
    big_nodes = data['user_tasks'] + data['script_tasks'] # 180 x 120

    #изменим flows, чтобы можно было искать их названия по ключам sourceRef
    flows = {}
    for flow in data['flows']:
        flows[ids[flow['sourceRef']]] = flows.get(ids[flow['sourceRef']], []) + [{
            'name': flow['name'],
            'bendpoints': flow.get('bendpoints'),
            'label': flow.get('label') 
        }]

    for lil in little_nodes:
        #text_deco - надпись для события, если событие стартовое, подписываем сверху, иначе - снизу 
        text_deco_placement = 1 if lil['id'] == 1 else -1
        nodes.append({
            'name': f"ID{ids[lil['name']]}",
            'x': str(lil['x']),
            'y': str(lil['y']),
            'width': '48',
            'height': '48',
            'transitions': flows.get(ids[lil['name']], []),
            'text_deco': (str(lil['x']), str(lil['y'] + 48 * text_deco_placement)),
        })

    for biggy in big_nodes:
        nodes.append({
            'name': f"ID{ids[biggy['name']]}",
            'x': str(biggy['x']),
            'y': str(biggy['y']),
            'width': '180',
            'height': '120',
            'transitions': flows.get(ids[biggy['name']], [])
        })

    return nodes