#!/usr/bin/env python3
import fiona
from flask import Flask, jsonify, request
from geopy.geocoders import Nominatim
from geopy.distance import vincenty
import utm


def get_entry(point):
    x, y = point["geometry"]["coordinates"]
    gps = utm.to_latlon(x, y, 32, 'U')

    return {"gps": gps,
            "details": point["properties"]["DettOgget"]}


def get_data(filename):
    with fiona.open(filename, 'r') as points:
        data = map(get_entry, points)
        return list(data)


def to_gps(q):
    geolocator = Nominatim()
    location = geolocator.geocode(q)
    if location:
        return (location.latitude, location.longitude)
    else:
        return None


def distance(a, b):
    return vincenty(a, b).meters


data = get_data("shapefiles/occupazione_suolo_pubblico_WGS84.shp")
app = Flask(__name__)


@app.route('/data')
def route_data():
    return jsonify(data)


@app.route('/gps')
def route_to_gps():
    q = request.args.get("q")
    gps = to_gps(q)
    return jsonify(gps)


@app.route('/')
def route_street():
    q = request.args.get("q")
    r = request.args.get("r")
    if not r:
        r = 1000
    gps = to_gps(q)
    response = [entry for entry in data
                if distance(gps, entry["gps"]) <= float(r)]
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
