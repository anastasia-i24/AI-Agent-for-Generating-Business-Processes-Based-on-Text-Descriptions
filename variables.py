import xml.dom.minidom as md

def variables(path, lanes, variables):
    file = md.parse(path)

    for l in lanes:
        lane = file.createElement('variable')
        lane.setAttribute('name', l['name'])
        lane.setAttribute('scriptingName', l['name'])
        lane.setAttribute('format', "ru.runa.wfe.var.format.ExecutorFormat")
        lane.setAttribute('swimlane', 'true')
        if l['editor'] != '0':
            lane.setAttribute('editor', l['editor'])
        file.firstChild.appendChild(variable)

    for v in variables:
        variable = file.createElement('variable')
        variable.setAttribute('name', v['name'])
        variable.setAttribute('scriptingName', v['name'])
        variable.setAttribute('format', f"ru.runa.wfe.var.format.{v['format']}Format")
        file.firstChild.appendChild(variable)

    with open(path, 'w', encoding='utf-8') as f:
        file.writexml(f, indent='', addindent='  ', newl='\n', encoding='utf-8')