from flask import Flask, render_template, request
import json
import shutil
import urllib
import os
import sc2reader
import mpyq
import heatmap
import hashlib
import Image
#from sqlalchemy import create_engine, Metadata, Table
#from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
#db = create_engine('sqlite:///blah')

@app.route('/sc2')
def sc2index():
    maps = open('static/maps.json')
    data = json.load(maps)
    
    return render_template('index.html', data=data)

@app.route('/sc2/map')
def map_detail():
    return render_template('map_detail.html')

@app.route('/sc2/replay', methods=['POST','GET'])
def replay_detail():
  # download replay
  replay_url = request.form["replay"]
  tempRep = urllib.urlretrieve(replay_url)
  shutil.move(tempRep[0], tempRep[0] + ".sc2replay")

  md5 = hashlib.md5()
  f = open(tempRep[0] + ".sc2replay", 'rb')
  for chunk in iter(lambda: f.read(8192), ''): 
    md5.update(chunk)
  replay_key = str(md5.hexdigest())

  replay = sc2reader.read_file(tempRep[0] + ".sc2replay")
  
  # determine which map we're on
  chksum = ""
  for entry in replay.raw["initData"]["map_data"]:
     chksum = chksum + str(entry)[52:len(str(entry))-2]

  maps = open('static/maps.json')
  all_maps = json.load(maps)
  for m in all_maps:
    if(all_maps[m]['checksum'] == chksum):
      replay_map = m  

  # Build event lists
  p1locations = list()
  p2locations = list()
  
  for event in replay.events:
     try:
       if (str(event.player)[7] == str(1)):
         p1locations.append(event.location)
       if (str(event.player)[7] == '2'):
         p2locations.append(event.location)
     except:
       pass
  mediapath = './static/img'

  # grab minimap
  minimap = Image.open(mediapath + replay_map.minimap)
  minimap = minimap.convert("RGBA")

   # run heatmap code
  hm = heatmap.Heatmap()
  hm.heatmap(p1locations, mediapath + replay_key + '.tmp.png', range=(replay_map.sizeX, replay_map.sizeY), dotsize=50, size=minimap.size)
  
  heat = Image.open(mediapath + replay_key + '.tmp.png')
#  heat = heat.resize(minimap.size) 
 
  out = Image.blend(minimap, heat, 0.5)
  out.save( mediapath + replay_key + '.jpg')
  
  return render_template('heatmap/replay.html', {'map': replay_map, 'replay_key': replay_key})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
