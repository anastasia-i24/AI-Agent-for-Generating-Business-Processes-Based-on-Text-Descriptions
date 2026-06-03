import xml.dom.minidom as md

def forms(path, data):
    events = data['events']
    tasks = data['user_tasks'] 
    ftl_files = []
    file = md.parse(path)
    root = file.getElementsByTagName('forms')[0]

    for event in events:
        if event['type'] == 'start':
            form = file.createElement('form')
            form.setAttribute('state', "ID1")
            form.setAttribute('file', "ID1.ftl")
            form.setAttribute('type', 'ftl')
            root.appendChild(form)

            generate_start_ftl(event)
            ftl_files.append("ID1.ftl")
            break

    for task in tasks:
        form = file.createElement('form')
        form.setAttribute('state', f"ID{task['id']}")
        form.setAttribute('file', f"ID{task['id']}.ftl")
        form.setAttribute('type', 'ftl')
        root.appendChild(form)

        generate_task_ftl(task)
        ftl_files.append(f"ID{task['id']}.ftl")

    with open(path, 'w', encoding='utf-8') as f:
        file.writexml(f, indent='', addindent='  ', newl='\n', encoding='utf-8')

    return ftl_files


def generate_task_ftl(task):
    ftl = '''
    <P style="text-align: center;"><STRONG>{name}</STRONG></P>
    <P>Сотрудник: ${{DisplayVariable("{lane}", "false")}}</P>'''
    with open(f'ID{task['id']}.ftl', "w", encoding="utf-8") as f:
        f.write(ftl.format(name=task['name'], lane=task['lane']))


def generate_start_ftl(start):
    ftl = '<P style="text-align: center;"><STRONG>{name}</STRONG></P>'
    with open(f'ID{start['id']}.ftl', "w", encoding="utf-8") as f:
        f.write(ftl.format(name=start['name']))