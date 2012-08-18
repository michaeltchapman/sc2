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

from sqlalchemy import create_engine, Column, String, Integer, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine  = create_engine('sqlite:///:memory:', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Map(Base):
    __tablename__= 'maps'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    filename = Column(String)
    sizeX = Column(Integer)
    sizeY = Column(Integer)
    checksum = Column(String)

    def __init__(self, name, filename, sizeX, sizeY, checksum):
        self.name = name
        self.filename = filename
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.checksum = checksum

Base.metadata.create_all(engine)

session.add_all([
    Map("Daybreak LE", "daybreak_le.png", 148, 120, "0b55c284749c2be7e71266cd4a49777c"),
    Map("Tal'darim Altar LE", "taldarim_altar.png", 176, 176, "b5a4cb90bd3e810ab1d4136a6098a6f9"),
    Map("Ohana LE", "ohana_le.png", 126, 132, "b547ac9bfeaf8444f22fc707c2618eb8"),
    Map("Antiga Shipyard", "antiga_shipyard.png", 132, 136,"30aa04f653fd33253fdbecbc5a7270a5"),
    Map("Entombed Valley", "entombed_valley.png", 148, 148, "fb7cfdb419fd8d667b84e66ca8dcec5e"),
    Map("Cloud Kingdom LE", "cloud_kingdom.png", 126, 132, "2e6116d40053f9989c2a6601feefc684"),
    Map("Condemned Ridge", "condemned_ridge.png", 208, 200, "a87a9e1b2bf397e44862aa5201901c82")
])

print session.dirty
print session.query(Map).filter_by(sizeX = 148).first().name
session.commit()

for m in session.query(Map, Map.name):
    print m

print session.query(func.count(Map.name)).scalar()    

def replay_detail(replay_url):
  # download replay
  #tempRep = urllib.urlretrieve(replay_url)
  #shutil.move(tempRep[0], tempRep[0] + ".sc2replay")

  #md5 = hashlib.md5()
  #f = open(tempRep[0] + ".sc2replay", 'rb')
  f = open(replay_url + ".sc2replay", 'rb')
  for chunk in iter(lambda: f.read(8192), ''): 
    md5.update(chunk)
  replay_key = str(md5.hexdigest())

  replay = sc2reader.read_file(replay_url + ".sc2replay")
  
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
  minimap = Image.open(mediapath + all_maps[replay_map]['filename'])
  minimap = minimap.convert("RGBA")

   # run heatmap code
  hm = heatmap.Heatmap()
  hm.heatmap(p1locations, mediapath + replay_key + '.tmp.png', range=(replay_map.sizeX, replay_map.sizeY), dotsize=50, size=minimap.size)
  
  heat = Image.open(mediapath + replay_key + '.tmp.png')
#  heat = heat.resize(minimap.size) 
 
  out = Image.blend(minimap, heat, 0.5)
  out.save( mediapath + replay_key + '.jpg')

#replay_url = 'http://sc2rep.com/replays/download/id/16288'

#tempRep = urllib.urlretrieve(replay_url)
#shutil.move(tempRep[0], tempRep[0] + ".sc2replay")


def buildjson():
    checksums = list()

    files = os.listdir('.')
    print "{"
    for f in files:
        n = f.split('.')
        if len(n) > 1 and n[1] == 'sc2replay':
            replay = sc2reader.read_file(f)
            chksum = ""
            for entry in replay.raw["initData"]["map_data"]:
                chksum = chksum + str(entry)[52:len(str(entry))-2]
            md5 = hashlib.md5()    
            md5.update(chksum)
            chksum = md5.hexdigest()
            if chksum not in checksums:
                checksums.append(chksum)
                print '\t' + "'" + replay.map + '":'
                print '\t' "{"
                print '\t\t' + '"size" : ' + '"xxx.xxx",'
                print '\t\t' + ' : ' + '"' + chksum + '",'
                print '\t' + "},"
                print ""
    print "}"
