a = [
    {'name': 'pupa', 'id': 'ID1'},
    {'name': 'zalupa', 'id': 'ID2'},
    {'name': 'biba', 'id': 'ID2'}
]
b = {}
for i in a:
    b[i['id'][2:]] = b.get(i['id'], []) + [i['name']]
print(b)