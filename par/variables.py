import xml.dom.minidom as md

def variables(path, data):
    lanes = data['lanes']
    variables = data['variables']
    file = md.parse(path)
    root = file.getElementsByTagName('variables')[0]

    for l in lanes:
        lane = file.createElement('variable')
        lane.setAttribute('name', l['name'])
        lane.setAttribute('scriptingName', l['name'])
        lane.setAttribute('format', "ru.runa.wfe.var.format.ExecutorFormat")
        lane.setAttribute('swimlane', 'true')
        root.appendChild(lane)

    for v in variables:
        variable = file.createElement('variable')
        variable.setAttribute('name', v['name'])
        variable.setAttribute('scriptingName', v['name'])
        variable.setAttribute('format', f"ru.runa.wfe.var.format.{v['format']}Format")
        root.appendChild(variable)

    with open(path, 'w', encoding='utf-8') as f:
        file.writexml(f, indent='', addindent='  ', newl='\n', encoding='utf-8')