import json
import joblib
import paho.mqtt.client as mqtt

# Load the trained model
model = joblib.load("fish_health_model.pkl")
print("Model loaded and ready for predictions.")

# MQTT configuration
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
SUB_TOPIC = "fish-tank/sensors"
PUB_TOPIC = "fish-tank/health"

# Called when client connects to broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker.")
        client.subscribe(SUB_TOPIC)
        print(f"Subscribed to topic: {SUB_TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}")

# Called when a message is received
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Received: {payload}")

        # Extract features
        pH = float(payload.get("pH"))
        temp = float(payload.get("temperature"))
        humidity = float(payload.get("humidity"))
        level = float(payload.get("water_level"))

        features = [[pH, temp, humidity, level]]

        # Predict
        prediction = model.predict(features)[0]
        status = "Healthy" if prediction == 1 else "Non-Healthy"

        print(f"Predicted status: {status}")

        # Publish result
        result = json.dumps({"status": status})
        client.publish(PUB_TOPIC, result)
        print(f"Published to {PUB_TOPIC}: {result}")

    except Exception as e:
        print(f"Error processing message: {e}")

# Set up MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
