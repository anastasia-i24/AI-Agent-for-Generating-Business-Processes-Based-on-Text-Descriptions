def gather_data():
    data = {
        'process_name': '',
        'user_tasks': [], 
        'script_tasks': [], 
        'lanes': [], 
        'events': [], 
        'flows': [],  
        'variables': [],
        "gateways": []
    }
    data['process_name'] = input('Введите название процесса: ')

    #собираем startEvent
    start = input("Введите название стартового события: ")
    initiator = input('Введите инициализатора бизнес-процесса: ')
    data['events'].append({'name': start, 'lane': initiator})
    if initiator:
        data['lanes'].append(initiator)

    #собираем userTask
    usertask = int(input("Введите количество usertask: "))
    for i in range(usertask):
        name = input(f"Введите название элемента usertask {i + 1}: ")
        lane = input(f"Введите название роли для элемента {name}: ")
        data['user_tasks'].append({'name': name, 'lane': lane})
        if lane not in data['lanes']:
            data['lanes'].append(lane)

    #собираем scriptTask
    scripttask = int(input("Введите количество scripttask: "))
    for i in range(scripttask):
        name = input(f"Введите название элемента scripttask {i + 1}: ")
        data['script_tasks'].append(name)

    #собираем оставшиеся роли
    print('Роли, добавленные на данный момент: ')
    print(*data['lanes'], sep='\n')
    print('Введите недостающие роли (если все роли добавлены, введите 0)')
    while (name := (input('Введите название роли: '))):
        if name == '0':
            break
        data['lanes'].append(name)

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
    data['events'].append({'name': end})

    #собираем переходы
    name = 1 #переходы будем называть "Переход{name}"
    print(f"Описываем переходы между элементами бизнес-процесса")
    #print(f"Ввод '1 2' означает 'элемент с id1 переходит в элемент с id2'")
    print(f"Чтобы завершить запись переходов введите 'done'")
    print(f"Список элементов, между которыми возможны переходы:")
    for event in data['events']:
        print(event['name'])
    for u_t in data['user_tasks']:
        print(u_t['name'])
    for s_t in data['script_tasks']:
        print(s_t)
    
    while (word := input().split()) != ['done']:
        sourceRef = word[0]
        targetRef = word[1]
        data['flows'].append({
            'name': f"Переход{name}", 
            'sourceRef': sourceRef, 
            'targetRef': targetRef
        })
        name += 1
        
    return data