import xml.dom.minidom as md

def variables(path, variables):
    file = md.parse(path)
    for name, items in variables.items():
        variable = file.createElement('variable')

        variable.setAttribute('name', name)
        variable.setAttribute('scriptingName', name)
        variable.setAttribute('format', f"ru.runa.wfe.var.format.{items['format']}Format")

        if items['format'] == 'Executor':
            variable.setAttribute('swimlane', 'true')
            if variables[name]['editor'] != '0':
                variable.setAttribute('editor', items['editor'])
    

        file.firstChild.appendChild(variable)

        with open(path, 'w', encoding='utf-8') as f:
            file.writexml(f, indent='', addindent='  ', newl='\n', encoding='utf-8')