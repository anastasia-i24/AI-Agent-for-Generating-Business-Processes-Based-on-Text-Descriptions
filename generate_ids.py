def generate_ids_exept_flows(data):
    events_exept_start = []
    for event in data['events']:
        if event['type'] == 'start':
            event['id'] = 1 #first id for startEvent
        else:
            events_exept_start.append(event)

    elements = data['user_tasks'] + data['script_tasks'] + data['lanes'] + events_exept_start + data['gateways'] 
    ID = 2
    for element in elements:
        element['id'] = ID
        ID += 1

    return data, ID


def generate_flow_ids(ID, flows):
    for flow in flows:
        flow['id'] = ID
        ID += 1

    return flows