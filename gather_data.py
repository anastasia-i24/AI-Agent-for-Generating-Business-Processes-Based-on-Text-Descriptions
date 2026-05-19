from llm import llm


def gather_data():
    user_data = []
    script_data = []
    lane_data = []
    flows = []
    variables = {}
    events = [["startEvent", [48, 48], '', 1], ["endEvent", [48, 48], '', 2]]
    data = [user_data, script_data, lane_data, events, flows, variables, "result", ""]
    current_id = 3

    print("Использовать LLM для генерации бизнес-процесса? да/yes чтобы подтвердить, иначе начинается ручная сборка")
    ans = input().strip().lower()
    if ans in {"да", "yes", "y"}:
        return llm(data)

    print("Введите название бизнес-процесса или оставьте строку пустой для result")
    process_name = input().strip()
    if process_name:
        data[6] = process_name

    print("Введите количество usertask")
    usertask = int(input())

    print("Введите количество scripttask")
    scripttask = int(input())

    for i in range(usertask):
        print(f"введите название элемента usertask {i + 1}")
        name = input().strip()

        print(f"введите X координату элемента {name}")
        x = int(input())
        print(f"введите Y координату элемента {name}")
        y = int(input())

        print(f"введите название lane для элемента {name}")
        lane = input().strip()

        user_data.append([name, [x, y], lane, current_id])
        current_id += 1

        if lane not in [item[0] for item in lane_data]:
            lane_data.append([lane, usertask + scripttask + 3 + len(lane_data)])
            variables[lane] = {"format": "Executor", "editor": "0"}

    for i in range(scripttask):
        print(f"введите название элемента scripttask {i + 1}")
        name = input().strip()

        print(f"введите X координату элемента {name}")
        x = int(input())
        print(f"введите Y координату элемента {name}")
        y = int(input())

        script_data.append([name, [x, y], current_id])
        current_id += 1

    print("Введите количество дополнительных ролей")
    roles = int(input())
    for i in range(roles):
        name = input("Введите название роли: ").strip()
        editor = input("Введите группу роли (если группы нет, введите 0): ").strip()
        variables[name] = {"format": "Executor", "editor": editor}
        if name not in [item[0] for item in lane_data]:
            lane_data.append([name, usertask + scripttask + 3 + len(lane_data)])

    vars_format = {
        1: "Boolean",
        2: "Long",
        3: "Double",
        4: "BigDecimal",
        5: "String",
        6: "Text",
        7: "Date",
        8: "DateTime",
        9: "Time",
        10: "File",
        11: "List",
    }

    print("Введите количество переменных")
    var_count = int(input())
    for i in range(var_count):
        name = input("Введите название переменной: ").strip()
        print("Выберите тип переменной:")
        print("1. Boolean")
        print("2. Long")
        print("3. Double")
        print("4. BigDecimal")
        print("5. String")
        print("6. Text")
        print("7. Date")
        print("8. DateTime")
        print("9. Time")
        print("10. File")
        print("11. List")
        format_number = int(input())

        item = {"format": vars_format[format_number]}
        if item["format"] == "List":
            print("Введите тип элемента списка: Boolean, Long, Double, BigDecimal, String, Text, Date, DateTime, Time, File, Executor")
            item["element_format"] = input().strip()

        default_value = input("Введите значение по умолчанию или оставьте строку пустой: ").strip()
        if default_value:
            item["default"] = default_value

        variables[name] = item

    print("описываем flow процессы")
    print("формат ввода '1 2' задача 1 переходит в задачу 2")
    print("чтобы завершить запись переходов введите 'done'")
    print("список возможных точек перехода и их айди")

    flow_id = 111112
    print("StartNode", " ", 1)
    print("EndNode", " ", 2)
    for item in user_data:
        print(item[0], "  ", item[3])
    for item in script_data:
        print(item[0], "  ", item[2])

    while True:
        word = input().split()
        if len(word) == 1:
            break

        source_ref = word[0]
        target_ref = word[1]
        flows.append([f"ID{flow_id}", f"tr{flow_id}", f"ID{source_ref}", f"ID{target_ref}"])
        flow_id += 1

    return data
