def gather_data():
    data = {
        'process_name': '',
        'user_tasks': [], 
        'script_tasks': [], 
        'lanes': [], 
        'events': [], 
        'flows': [],  
        'variables': []
    }
    id = 1
    existing_lanes = [] # будем проверять, есть ли lane тут, чтобы не добавлять в lanes дважды одно и то же
    data['process_name'] = input('Введите название процесса: ')

    #собираем startEvent
    start = input("Введите название стартового события: ")
    x = int(input(f"Введите X координату стартового события: "))
    y = int(input(f"Введите Y координату стартового события: "))
    initiator = input('Введите инициализатора бизнес-процесса (если его нет, введите 0): ')
    data['events'].append({'name': start, 'x': x, 'y': y, 'lane': initiator, 'id': id})
    id += 1
    if initiator != '0':
        existing_lanes.append(initiator)
        initiator_editor = input('Введите группу роли (если группы нет введите 0): ')
        data['lanes'].append({'name': initiator, 'id': id, 'editor': initiator_editor})
        id += 1

    #собираем userTask
    usertask = int(input("Введите количество usertask: "))
    for i in range(usertask):
        name = input(f"Введите название элемента usertask {i + 1}: ")
        x = int(input(f"Введите X координату элемента {name}: "))
        y = int(input(f"Введите Y координату элемента {name}: "))
        lane = input(f"Введите название роли для элемента {name}: ")
        data['user_tasks'].append({'name': name, 'x': x, 'y': y, 'lane': lane, 'id': id})
        id += 1
        if lane not in existing_lanes:
            existing_lanes.append(lane)
            editor = input('Введите группу роли (если группы нет введите 0): ')
            data['lanes'].append({'name': lane, 'id': id, 'editor': editor})
            id += 1

    #собираем scriptTask
    scripttask = int(input("Введите количество scripttask: "))
    for i in range(scripttask):
        name = input(f"Введите название элемента scripttask {i + 1}: ")
        x = int(input(f"Введите X координату элемента {name}: "))
        y = int(input(f"Введите Y координату элемента {name}: "))
        data['script_tasks'].append({'name': name, 'x': x, 'y': y, 'id': id})
        id += 1

    #собираем оставшиеся роли
    print('Роли, добавленные на данный момент: ')
    print(*existing_lanes, sep='\n')
    print('Введите недостающие роли (если все роли добавлены, введите 0)')
    while (name := (input('Введите название роли: '))):
        if name == '0':
            break
        editor = input('Введите группу роли (если группы нет введите 0): ')
        data['lanes'].append({'name': name, 'id': id, 'editor': editor})
        id += 1

    #собираем переменные
    vars_format = {
        1: 'Boolean',
        2: 'Long',
        3: 'Double',
        4: 'BigDecimal',
        5: 'String',
        6: 'Text',
        7: 'Date',
        8: 'DateTime',
        9: 'Time',
        10: 'File'
    }
    var_s = int(input('Введите количество переменных: '))
    for i in range(var_s):
        name = input('Введите название переменной: ')
        print('Выберите тип переменной (введите соответствующее типу число):\n')
        print('1. Логическое значение (true/false)',
              '2. Целое число',
              '3. Дробное число',
              '4. Число повышенной точности',
              '5. Строка (одна строка)',
              '6. Текст (многострочный)',
              '7. Дата (без времени)',
              '8. Дата и время',
              '9. Время',
              '10. Файл', sep='\n')
        format = int(input())
        data['variables'].append({'name': name, 'format': vars_format[format]})

    #собираем endEvent
    end = input("Введите название конечного события: ")
    x = int(input(f"Введите X конечного события: "))
    y = int(input(f"Введите Y координату конечногособытия: "))
    data['events'].append({'name': end, 'x': x, 'y': y, 'id': id})
    id += 1

    #собираем переходы
    name = 1 #переходы будем называть "Переход{name}"
    print(f"Описываем переходы между элементами бизнес-процесса")
    print(f"Ввод '1 2' означает 'элемент с id1 переходит в элемент с id2'")
    print(f"Чтобы завершить запись переходов введите 'done'")
    print(f"Список элементов, между которыми возможны переходы:")
    for event in data['events']:
        print(event['name'], event['id'])
    for u_t in data['user_tasks']:
        print(u_t['name'], u_t['id'])
    for s_t in data['script_tasks']:
        print(s_t['name'], s_t['id'])
    
    while (word := input().split()) != ['done']:
        sourceRef = int(word[0])
        targetRef = int(word[1])
        data['flows'].append({
            'id': id, 
            'name': f"Переход{name}", 
            'sourceRef': sourceRef, 
            'targetRef': targetRef
        })
        id += 1
        name += 1
        
    return data