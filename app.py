from flask import Flask, render_template
import json
#from sqlalchemy import create_engine, Metadata, Table
#from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
#db = create_engine('sqlite:///blah')

@app.route('/sc2')
def sc2index():
    maps = open('static/maps.json')
    data = json.load(maps)
    
    return render_template('index.html', data=data)

@app.route('/sc2/replay')
def replay_detail():
    return render_template('replay_detail.html')

@app.route('/sc2/map')
def map_detail():
    return render_template('map_detail.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
