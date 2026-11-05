import json
import paho.mqtt.client as mqtt
from pymongo import MongoClient
from datetime import datetime

# MongoDB setup
client_mongo = MongoClient("mongodb://localhost:27017")
db = client_mongo["fish_tank"]
collection = db["logs"]

# Cache to hold latest sensor reading until health status arrives
latest_sensor_data = {}

# MQTT setup
MQTT_BROKER = "broker.emqx.io"
TOPIC_SENSOR = "fish-tank/sensors"
TOPIC_HEALTH = "fish-tank/health"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker.")
        client.subscribe([(TOPIC_SENSOR, 0), (TOPIC_HEALTH, 0)])
        print(f"Subscribed to: {TOPIC_SENSOR} and {TOPIC_HEALTH}")
    else:
        print("Failed to connect. Code:", rc)

def on_message(client, userdata, msg):
    global latest_sensor_data

    topic = msg.topic
    payload = json.loads(msg.payload.decode())
    print(f"Received on {topic}: {payload}")

    if topic == TOPIC_SENSOR:
        # Store latest sensor reading
        latest_sensor_data = payload
        latest_sensor_data["timestamp"] = datetime.utcnow()

    elif topic == TOPIC_HEALTH and latest_sensor_data:
        # Append health status to latest sensor data
        latest_sensor_data["status"] = payload.get("status", "Unknown")

        # Save to MongoDB
        collection.insert_one(latest_sensor_data)
        print("Stored to MongoDB:", latest_sensor_data)

        # Clear cache
        latest_sensor_data = {}

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, 1883, 60)
client.loop_forever()
