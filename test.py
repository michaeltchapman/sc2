import json

maps = open('static/maps.json')
data = json.loads(maps.read())
print data['Ohana LE']
