from flask import request
from flask_restful import Resource, reqparse, abort, inputs
from flask_restful import Resource, fields, marshal_with

from . import api
from ..models import SensorReading


resource_fields = {
    'room': fields.String(attribute='room'),
    'temperature': fields.Float,
    'humidity': fields.Float,
    'date': fields.String
}

parser = reqparse.RequestParser()
parser.add_argument('date',type=inputs.datetime_from_iso8601 , 
    help="<date> has to be in datetime isoformat: 2018-01-05T15:48:11.893728 `datetime.datetime.now().isoformat()`")
parser.add_argument('room',type=inputs.regex('^\D+$')  , 
    help="<room> has to be a word 'string'")
parser.add_argument('temperature',type=float , 
    help="<temperature> has to be a number 'float'")
parser.add_argument('humidity',type=float , 
    help="<temperature> has to be a number 'float'")


# curl http://localhost:5000/thermohygro -H "Content-Type: application/json" -d '{ "date" : "2018-01-05T15:48:11.893728+00:00",  "room" : "bedroom", "temperature" : 25, "humidity" : 51 }' -X POST 
# Python can generate this date: 
# datetime.datetime.now().isoformat()

def find_reading_by_id(reading_id):
    '''
    Return database reading by id
    '''
    for reading in SensorReading.objects(readingid=reading_id):
        return reading


def abort_if_data_doesnt_exist(reading_id):
    reading = find_reading_by_id(reading_id)
    if not reading:
        abort(404, message="Sensor reading {} doesn't exist".format(reading_id))
    return reading


def return_all():
    readings = []
    for reading in SensorReading.objects:
        #TODO: Create resource_fields for returning a list of dictionaries from a list of reading objects 
        readings.append(reading._data)
    return readings


class Reading(Resource):
    @marshal_with(resource_fields)
    def get(self, reading_id):
        reading = abort_if_data_doesnt_exist(reading_id)
        
        return reading, 200

    @marshal_with(resource_fields)
    def delete(self, reading_id):
        reading = abort_if_data_doesnt_exist(reading_id)
        reading.delete

        return "{'message' : 'Data was deleted' }", 204

    # Intended to update temperature and humidity only, date and room are readonly
    @marshal_with(resource_fields)
    def put(self, reading_id):
        args = parser.parse_args()
        reading = abort_if_data_doesnt_exist(reading_id)

        reading.temperature = args['temperature']
        reading.humidity = args['humidity']
        
        reading.save

        return reading, 201


class ReadingList(Resource):
    #TODO: Create resource_fields for returning a list of dictionaries from a list of reading objects 
    def get(self):
        return return_all()

    @marshal_with(resource_fields)
    def post(self, **kwargs):
        args = parser.parse_args()
        room =  args['room']
        date = args['date']
        reading_id = "{0}{1}".format(room, date.strftime("%Y%M%d%H%m%S%f"))

        reading = SensorReading( 
                        readingid = reading_id,
                        date = str(date),
                        room = room,
                        temperature = args['temperature'],
                        humidity = args['humidity']
        )
        reading.save()
            
        return reading, 201
