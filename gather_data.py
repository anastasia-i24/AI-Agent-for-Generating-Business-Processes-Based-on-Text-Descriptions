import json

def gather_data():
    print(f"Введите количество usertask")
    usertask = int(input())

    print(f"Введите количество scripttask")
    scripttask = int(input())

    events = [["startEvent", [48, 48], '' ,1], ["endEvent", [48, 48], '', 2]]
    user_data = []
    script_data = []
    lane_data = []
    flows = []
    variables = {}
    data = [user_data, script_data, lane_data, events, flows, variables]
    id = 3

    for i in range(usertask):
        data[0].append([])
        print(f"введите название элемента usertask {i + 1}")
        name = str(input())
        data[0][-1].append(name)

        coords = []
        print(f"введите X координату элемента {name}")
        coords.append(int(input()))
        print(f"введите Y координату элемента {name}")
        coords.append(int(input()))
        data[0][-1].append(coords)

        print(f"введите название lane для элемента {name}")
        lane = str(input())
        data[0][-1].append(lane)
        data[0][-1].append(id)
        id+=1
        lane_data.append([lane, usertask+scripttask+3+len(lane_data)])

    for i in range(scripttask):
        data[1].append([])
        print(f"введите название элемента scripttask {i + 1}")
        name = str(input())
        data[1][-1].append(name)

        coords = []
        print(f"введите X координату элемента {name}")
        coords.append(int(input()))
        print(f"введите Y координату элемента {name}")
        coords.append(int(input()))
        data[1][-1].append(coords)
        data[1][-1].append(id)
        id+=1

    #собираем роли
    roles = int(input('Введите количество ролей: '))
    for i in range(roles):
        name = input('Введите название роли: ')
        editor = input('Введите группу роли (если группы нет введите 0): ')
        variables[name] = {'format': 'Executor', 'editor': editor}

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
        variables[name] = {'format': vars_format[format]}

    print(f"описываем flow процессы")
    print(f"формат ввода '1 2' задача 1 переходит в задачу 2")
    print(f"чтобы завершить запись переходов введите 'done'")
    print(f"список возможных точек перехода и их айди")
    # add ID to id
    id = "111112"
    # add tr to name
    name = "111112"
    print("StartNode", " " , 1)
    print("EndNode", " " , 2)
    for i in data[0]:
        print(i[0], "  ", i[3])
    for i in data[1]:
        print(i[0], "  ", i[2])
    while True:
        word = str(input()).split()
        if len(word) == 1:
            break

        sourceRef = word[0]
        targetRef = word[1]
        flows.append(["ID" + id,"tr" + name,"ID" + sourceRef, "ID" + targetRef])
        id = str(int(id) + 1)
        name = str(int(name) + 1)
        
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)