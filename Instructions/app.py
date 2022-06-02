import numpy as np
import datetime as dt
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Station=Base.classes.station
measurement = Base.classes.measurement

app = Flask(__name__)

@app.route("/")
def home_page():
    return(
        f"Available Routes:<br/>"
        f"Precipitaion: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Tobs: /api/v1.0/tobs<br/>"
        f"Temperature from start date: /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature from start to end date: /api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    year_ago_data=session.query(measurement.date, measurement.prcp).filter(measurement.date > '2016-08-22')
    year_ago_data_df=pd.DataFrame(year_ago_data, columns=['date','prcp'])
    index_date=year_ago_data_df.set_index('date')
    session.close()
    precipitation=list(np.ravel(index_date))
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    results=session.query(Station.station, Station.name).all()
    session.close()
    stations_list=list(np.ravel(results))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)
    latest_date=session.query(measurement.date).order_by(measurement.date.desc()).first()
    one_year_earlier=dt.date(2017,8,23) - dt.timedelta(days=365)
    results=session.query(*[measurement.date, measurement.tobs]).filter(measurement.date>=one_year_earlier).all()
    session.close()
    tobs=list(np.ravel(results))
    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def start(start):
    session=Session(engine)
    result=session.query(func.avg(measurement.tobs), func.max(measurement.tobs), func.min(measurement.tobs)).filter(measurement.date>start).all()
    session.close()
    tob_start=[]
    for min,max,avg in result:
        tob_start_df={}
        tob_start_df['avg']=avg
        tob_start_df['max']=max
        tob_start_df['min']=min
        tob_start.append(tob_start_df)

    return jsonify(tob_start)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session=Session(engine)
    result=session.query(func.avg(measurement.tobs), func.max(measurement.tobs), func.min(measurement.tobs)).filter(measurement.date>=start).filter(measurement.date<=end).all()
    session.close()

    tob_start_end=[]
    for max,min,avg in result:
         tob_start_end_df={}
         tob_start_end_df['avg']=avg
         tob_start_end_df['max']=max
         tob_start_end_df['min']=min
         tob_start_end.append(tob_start_end_df)
        
    return jsonify(tob_start_end)

if __name__ == '__main__':
    app.run(debug=True, port=5000)