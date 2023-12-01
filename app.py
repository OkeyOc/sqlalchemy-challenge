# Import the dependencies.
import datetime as dt
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import inspect
import numpy as np
import pandas as pd
import os

#################################################
# Database Setup
os.chdir(os.path.dirname(os.path.realpath(__file__)))
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
#################################################

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
#################################################
# Flask Setup
app=Flask(__name__)
#################################################
main_session = Session(engine)
    #query to retrieve the last 12 months of precipitation data.
first_date = main_session.query(Measurement.date).order_by((Measurement.date)).limit(1).all()
last_date = main_session.query(Measurement.date).order_by((Measurement.date).desc()).limit(1).all()
last_12mnth = (dt.datetime.strptime(last_date[0][0], '%Y-%m-%d') - dt.timedelta(days=365)).date()
main_session.close()
# Flask Routes
@app.route("/")
def welcome():
    return (
        f"<p>Alohaaa Welina to the Hawaii weather API!!!!!!</p>"
        f"<p>All routes available:</p>"
        f"/api/v1.0/precipitation<br/>Returns a JSON representation of percipitation data for the dates between {last_12mnth} and {last_date[0][0]}<br/><br/>"
        f"/api/v1.0/stations<br/>Returns a JSON list of the weather stations<br/><br/>"
        f"/api/v1.0/tobs<br/>Returns a JSON list of the Temperature Observations (tobs) for each station for the dates between {last_12mnth} and {last_date[0][0]}<br/><br/>"
        f"/api/v1.0/yourstartdate(yyyy-mm-dd)<br/>Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for the dates from the given start date in yyyy-mm-dd format <br/><br/>."
        f"/api/v1.0/start_date(yyyy-mm-dd)/end_date(yyyy-mm-dd)<br/>Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for the dates between the given start date and end date<br/><br/>."
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    #query to retrieve the last 12 months of precipitation data.
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_12mnth)\
        .filter(Measurement.station == Station.station).all()
    session.close()
    #Convert the query results to a Dictionary using date as the key and prcp as the value.
    prcp_totals = []
    for result in results:
        row = {}
        row["date"] = result[0]
        row["prcp"] = result[1]
        prcp_totals.append(row)
    #Return the JSON representation of your dictionary.
    session.close()
    return jsonify(prcp_totals)


@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    print("station status:OK")
    #a query to get the stations.
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    #Return a JSON list of stations from the dataset.
    session.close()
    return jsonify(stations.to_dict())

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    print("tobs status:OK")
    #query for the dates and temperature observations from a year from the last data point
    tobs_results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= last_12mnth).order_by(Measurement.date).all()
    # Create a list of dicts with `date` and `tobs` as the keys and values
    tobs_totals = []
    for result in tobs_results:
        row = {}
        row["date"] = result[0]
        row["tobs"] = result[1]
        tobs_totals.append(row)
    #Return a JSON list of Temperature Observations (tobs) for the previous year.
    session.close()
    return jsonify(tobs_totals)


@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    print("start_date status:OK")
#convert the tsring from user to date
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    last_date_dd = (dt.datetime.strptime(last_date[0][0], '%Y-%m-%d')).date() 
    first_date_dd = (dt.datetime.strptime(first_date[0][0], '%Y-%m-%d')).date()
#if fgiven start_date greater than last or lesser than first available date in dataset, print the following 
    if start_date > last_date_dd or start_date < first_date_dd:
        return(f"Select date range between {first_date[0][0]} and {last_date[0][0]}")
    else:
       #Return a JSON list of the minimum temperature, the average temperature, 
        #and the max temperature for a given start range.
        start_min_max_temp = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
            func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
        start_date_data = list(np.ravel(start_min_max_temp))
        session.close()
        return jsonify(start_date_data)


@app.route("/api/v1.0/<start>/<end>")
def end_date(start,end):
    session = Session(engine)
    print("start and end status:OK")
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    last_date_dd = (dt.datetime.strptime(last_date[0][0], '%Y-%m-%d')).date() 
    first_date_dd = (dt.datetime.strptime(first_date[0][0], '%Y-%m-%d')).date()
    if start_date > last_date_dd or start_date < first_date_dd or end_date > last_date_dd or\
                  end_date < first_date_dd:
        return(f"Select date range between {first_date[0][0]} and {last_date[0][0]}")
    else:
    #Return a JSON list of the minimum temperature, the average temperature, 
    #and the max temperature for a given start-end range.
        start_end_min_max_temp = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
         func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
        start_end_data = list(np.ravel(start_end_min_max_temp))
        session.close()
        return jsonify(start_end_data)
    
if __name__=="__main__":
    app.run(debug=True)