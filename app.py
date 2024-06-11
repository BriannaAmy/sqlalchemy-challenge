# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    queryDate = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    prcpData = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= queryDate).all()
    session.close()
    precipitation = []
    for date, prcp in prcpData:
        prcpDict = {}
        prcpDict["date"] = date
        prcpDict["precipitation"] = prcp
        precipitation.append(prcpDict)
    
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.station).all()
    session.close()
    stationList = list(np.ravel(stations))
    return jsonify(stationList)

@app.route("/api/v1.0/tobs")
def temps():
    queryDate = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    tempData = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= queryDate).all()
    session.close()
    tempList = list(np.ravel(tempData))
    return jsonify(tempList)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    selection = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end:
        startDate = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*selection).filter(Measurement.date >= startDate).all()
        session.close()
        tempList = list(np.ravel(results))
        return jsonify(tempList)
    else:
        startDate = dt.datetime.strptime(start, "%m%d%Y")
        endDate = dt.datetime.strptime(end, "%m%d%Y")
        results = session.query(*selection).filter(Measurement.date >= startDate).filter(Measurement.date <= endDate).all()
        session.close()
        tempList = list(np.ravel(results))
        return jsonify(tempList)

if __name__ == "__main__":
    app.run(debug=True)