#!/usr/bin/python

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import datetime
import json
import time
import ssl

import jwt
import paho.mqtt.client as mqtt

from Adafruit_BME280 import *
import RPi.GPIO as GPIO

FAN_GPIO = 21
sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

# Update and publish temperature readings at a rate of SENSOR_POLL per second.
SENSOR_POLL=5

def create_jwt(project_id, private_key_file, algorithm):
  """Create a JWT (https://jwt.io) to establish an MQTT connection."""
  token = {
      'iat': datetime.datetime.utcnow(),
      'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
      'aud': project_id
  }
  with open(private_key_file, 'r') as f:
    private_key = f.read()
  print 'Creating JWT using {} from private key file {}'.format(
      algorithm, private_key_file)
  return jwt.encode(token, private_key, algorithm=algorithm)


def error_str(rc):
  """Convert a Paho error to a human readable string."""
  return '{}: {}'.format(rc, mqtt.error_string(rc))


class Device(object):
  """Represents the state of a single device."""

  def __init__(self):
    self.temperature = 0
    self.fan_on = False
    self.connected = False

  def update_sensor_data(self):
    self.temperature = int(sensor.read_temperature())

  def wait_for_connection(self, timeout):
    """Wait for the device to become connected."""
    total_time = 0
    while not self.connected and total_time < timeout:
      time.sleep(1)
      total_time += 1

    if not self.connected:
      raise RuntimeError('Could not connect to MQTT bridge.')

  def on_connect(self, unused_client, unused_userdata, unused_flags, rc):
    """Callback for when a device connects."""
    print 'Connection Result:', error_str(rc)
    self.connected = True

  def on_disconnect(self, unused_client, unused_userdata, rc):
    """Callback for when a device disconnects."""
    print 'Disconnected:', error_str(rc)
    self.connected = False

  def on_publish(self, unused_client, unused_userdata, unused_mid):
    """Callback when the device receives a PUBACK from the MQTT bridge."""
    print 'Published message acked.'

  def on_subscribe(self, unused_client, unused_userdata, unused_mid,
                   granted_qos):
    """Callback when the device receives a SUBACK from the MQTT bridge."""
    print 'Subscribed: ', granted_qos
    if granted_qos[0] == 128:
      print 'Subscription failed.'

  def on_message(self, unused_client, unused_userdata, message):
    """Callback when the device receives a message on a subscription."""
    payload = message.payload
    print "Received message '{}' on topic '{}' with Qos {}".format(
        payload, message.topic, str(message.qos))

    # The device will receive its latest config when it subscribes to the config
    # topic. If there is no configuration for the device, the device will
    # receive an config with an empty payload.
    if not payload:
      return

    # The config is passed in the payload of the message. In this example, the
    # server sends a serialized JSON string.
    data = json.loads(payload)
    if data['fan_on'] != self.fan_on:
      # If we're changing the state of the fan, print a message and update our
      # internal state.
      self.fan_on = data['fan_on']
      if self.fan_on:
        GPIO.output(FAN_GPIO, GPIO.HIGH)
        print 'Fan turned on.'
      else:
        GPIO.output(FAN_GPIO, GPIO.LOW)
        print 'Fan turned off.'


def parse_command_line_args():
  """Parse command line arguments."""
  parser = argparse.ArgumentParser(
      description='Example Google Cloud IoT MQTT device connection code.')
  parser.add_argument(
      '--project_id', required=True, help='GCP cloud project name')
  parser.add_argument(
      '--registry_id', required=True, help='Cloud IoT registry id')
  parser.add_argument('--device_id', required=True, help='Cloud IoT device id')
  parser.add_argument(
      '--private_key_file', required=True, help='Path to private key file.')
  parser.add_argument(
      '--algorithm',
      choices=('RS256', 'ES256'),
      required=True,
      help='Which encryption algorithm to use to generate the JWT.')
  parser.add_argument(
      '--cloud_region', default='us-central1', help='GCP cloud region')
  parser.add_argument(
      '--ca_certs',
      default='roots.pem',
      help='CA root certificate. Get from https://pki.google.com/roots.pem')
  parser.add_argument(
      '--num_messages',
      type=int,
      default=100,
      help='Number of messages to publish.')
  parser.add_argument(
      '--mqtt_bridge_hostname',
      default='mqtt.googleapis.com',
      help='MQTT bridge hostname.')
  parser.add_argument(
      '--mqtt_bridge_port', default=8883, help='MQTT bridge port.')

  return parser.parse_args()


def main():
  args = parse_command_line_args()

  # Setup GPIOs for the RasPi3 and cobbler
  GPIO.setmode(GPIO.BCM) 
  GPIO.setup(FAN_GPIO, GPIO.OUT)

  # Create our MQTT client and connect to Cloud IoT.
  client = mqtt.Client(
      client_id='projects/{}/locations/{}/registries/{}/devices/{}'.format(
          args.project_id, args.cloud_region, args.registry_id, args.device_id))
  client.username_pw_set(
      username='unused',
      password=create_jwt(args.project_id, args.private_key_file,
                          args.algorithm))
  client.tls_set(ca_certs=args.ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

  device = Device()

  client.on_connect = device.on_connect
  client.on_publish = device.on_publish
  client.on_disconnect = device.on_disconnect
  client.on_subscribe = device.on_subscribe
  client.on_message = device.on_message

  client.connect(args.mqtt_bridge_hostname, args.mqtt_bridge_port)

  client.loop_start()

  # This is the topic that the device will publish telemetry events (temperature
  # data) to.
  mqtt_telemetry_topic = '/devices/{}/events'.format(args.device_id)

  # This is the topic that the device will receive configuration updates on.
  mqtt_config_topic = '/devices/{}/config'.format(args.device_id)

  # Wait up to 5 seconds for the device to connect.
  device.wait_for_connection(5)

  # Subscribe to the config topic.
  client.subscribe(mqtt_config_topic, qos=1)

  # Update and publish temperature readings at a rate of one per second.
  for _ in range(args.num_messages):
    device.update_sensor_data()

    # Report the device's temperature to the server, by serializing it as a JSON
    # string.
    payload = json.dumps({'temperature': device.temperature})
    print 'Publishing payload', payload
    client.publish(mqtt_telemetry_topic, payload, qos=1)
    time.sleep(SENSOR_POLL)

  client.disconnect()
  client.loop_stop()
  GPIO.cleanup()
  print 'Finished loop successfully. Goodbye!'


if __name__ == '__main__':
  main()
