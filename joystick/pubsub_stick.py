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

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

from subprocess import call

# Software SPI configuration:
CLK  = 12
MISO = 23
MOSI = 24
CS   = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

servoMin = 50
servoMax = 250
servoSteps = servoMax - servoMin
stickSensitivity = 5   # the lower the number the more sensitive we are to stick changes that transmit a message
stickToServoPositionRatio = 1024/float(servoSteps) # assume 10bit ADC

#Servo settings
# pwmGPIO = "18"
# pwmClock = "192"
# pwmRange = "2000"

# Update and publish readings at a rate of SENSOR_POLL per second.
SENSOR_POLL=0
SENSOR_DEBOUNCE=0.1

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
    #self.leftright = 512
    #self.updown = 512
    self.servoStep = 150
    self.connected = False
    # self.acked = True

  def update_sensor_data(self):
    leftRightServoStep = self.servoStep
    #self.leftright = mcp.read_adc(0)
    #self.updown = mcp.read_adc(1)
    # while self.acked == False:
    # pass
    # print "."
    #self.acked = False

    #print 'leftRightServoStep', leftRightServoStep
    #poll until the stick moves
    while leftRightServoStep == self.servoStep:
      leftRightServoStepPreDeb = mcp.read_adc(0)/stickToServoPositionRatio
      time.sleep(SENSOR_DEBOUNCE)
      leftRightServoStepPostDeb = mcp.read_adc(0)/stickToServoPositionRatio
      if leftRightServoStepPreDeb == leftRightServoStepPostDeb:
        leftRightServoStep = int(leftRightServoStepPreDeb/stickSensitivity)*stickSensitivity
        leftRightServoStep = leftRightServoStep + servoMin

    #print 'leftRightServoStep', leftRightServoStep
    self.servoStep = leftRightServoStep

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
    # self.acked = True
    print 'Published message acked.'

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

  # print "stickToServoPositionRatio", stickToServoPositionRatio
  #setup PWM for servo
  # err = call(["gpio", "-g", "mode", pwmGPIO, "pwm"])
  # err |= call(["gpio", "pwm-ms"])
  # err |= call(["gpio", "pwmc", pwmClock])
  # err |= call(["gpio", "pwmr", pwmRange])
  # if err != 0:
  #   print "gpio setup error:", err
  #   quit()

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

  client.connect(args.mqtt_bridge_hostname, args.mqtt_bridge_port)

  client.loop_start()

  # This is the topic that the device will publish telemetry events to.
  mqtt_telemetry_topic = '/devices/{}/events'.format(args.device_id)

  # This is the topic that the device will receive configuration updates on.
  mqtt_config_topic = '/devices/{}/config'.format(args.device_id)

  # Wait up to 5 seconds for the device to connect.
  device.wait_for_connection(5)

  # Subscribe to the config topic.
  client.subscribe(mqtt_config_topic, qos=1)

  # Update and publish stick position readings at a rate of one per SENSOR_POLL but poll the sensor for "stickSensitivity" changes.
  for _ in range(args.num_messages):
    # In an actual device, this would read the device's sensors. 
    device.update_sensor_data()

    # Report the joystick's position to the server, by serializing it as a JSON
    # string.
    payload = json.dumps({'servoStep': device.servoStep})
    print 'Publishing payload', payload
    client.publish(mqtt_telemetry_topic, payload, qos=1)
    time.sleep(SENSOR_POLL)

  client.disconnect()
  client.loop_stop()
  print 'Finished loop successfully. Goodbye!'


if __name__ == '__main__':
  main()
