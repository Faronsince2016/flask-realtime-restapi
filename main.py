from realtimeapp import configure_app, app, create_api
from realtimeapp.socketio import create_socketio, socketio
from mongoengine import connect
from os import environ

# Initialise app
app = configure_app()

# Initialise restful api
create_api(app)

# Initialise flask-socketio
create_socketio(app)

if not environ.get('FLASK_DEBUG', None): 
    mongodb_location = environ.get('MONGODB_NETWORK_ALIAS', "localhost")
    connect('mongoengine', host=mongodb_location, port=27017)
    print('Connected to MongoDB instance in ', mongodb_location)
    print('If you are testing and need a mock database use: $ export FLASK_DEBUG=1')
else:
    connect('mongoengine_test', is_mock=True)
    print('Connected to mock database.')

#TODO: Run this on debug only?
from realtimeapp.models import Sensor
# The default sensor, for testing purposes
sensor1 = Sensor(name='sensor', room='room')
sensor1.save()


if __name__ == '__main__':
    # the start point is socketio.run() uses eventlet which provides a production ready 
    # Establishing a Connection

    socketio.run(app)
