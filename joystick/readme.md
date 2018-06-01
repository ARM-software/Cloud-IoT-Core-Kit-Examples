This example will use the kit's servo and joystick in a complete IoT system with both server and device component(s). The devices in this system (your Cloud IoT Core kit(s) in this case) publish the joystick position (e.g. a dimmable light switch or mobile application control) data on its pubsub registry feed and individual device ID. A server python application, which you can run from any machine you like, consumes the telemetry data from your cloud Pub/Sub registery, topic and events. The server transmits the servo position to a device via a Cloud IoT Core configuration update. In this case, it transmits back to our Pi but it could be any number of devices; e.g. light bulbs, HVAC vents and fans, etc.

Connect the RasPi Cobbler board to your breadboard and the 40 pin cable to your Pi 3 [as pictured here](https://cdn-shop.adafruit.com/970x728/2029-01.jpg). The keyed end in the cobbler is obvious, the white striped end of the cable and 90° angle of the cable coming off the RasPi (which is not keyed) are useful visual queues.

This example requires the [included 10-bit ADC (MCP3008) to be connected via software SPI to the Pi](https://github.com/ARM-software/Cloud-IoT-Core-Kit-Examples/blob/master/joystick/joystick_wiring.png?raw=true) in order to read the joystick position. Follow [this guide](https://learn.adafruit.com/raspberry-pi-analog-to-digital-converters/mcp3008) for setting up software SPI. Please note, if you're using the same Pi to control both the servo and read the joystick, the servo must use GPIO 18 for pulse width modulation (PWM) so we'll be using GPIO 12 as our clock pin in this SPI setup.

Install the Adafruit Python MCP3008 driver from GitHub as requested in the aforementioned setup guide in order to get the "simpletest.py" example code to debug your wiring. You'll have to change simpletest.py to use GPIO12 as the clock. You can pull any of the channels (0-7) up or down to test your wiring or just jump to hooking up the joystick and use that to test.

    sudo apt-get install build-essential python-dev python-smbus git
    cd ~ && mkdir dev
    cd dev
    git clone https://github.com/adafruit/Adafruit_Python_MCP3008.git
    cd Adafruit_Python_MCP3008
    sudo python setup.py install

[Connect the joystick to the breadboard](https://github.com/ARM-software/Cloud-IoT-Core-Kit-Examples/blob/master/joystick/joystick_wiring.png?raw=true), the L/R+ to the 3.3v power rail, GND to the ground rail and L/R to CH0 on the MCP3008 ADC. You can also connect U/D to CH1 if you like but we'll only be using left and right in this example. In your Adafruit_Python_MCP3008/examples directory, you can now run:

    cd examples
    
edit GPIO 18 to 12 with your favorite editor
    
    python simpletest.py
   

Changes in the L/R stick position should show up as values between 0 to 1024.

[Connect the servo](https://github.com/ARM-software/Cloud-IoT-Core-Kit-Examples/blob/master/joystick/joystick_wiring.png?raw=true) by wiring the brown wire to the ground rail, the red wire to the 5v rail or horizontal row and the orange wire to GPIO 18. Adafruit has an [explaination of the pulse width modulation](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-8-using-a-servo-motor/software) (PWM) settings we'll use to below to test your wiring. Raspbian has a gpio command included so testing from your shell is easy. Configure with:
    
    gpio -g mode 18 pwm
    gpio pwm-ms
    gpio pwmc 192
    gpio pwmr 2000

Move the servo to the middle, left and right:
    
    gpio -g pwm 18 150
    gpio -g pwm 18 50
    gpio -g pwm 18 250

You'll need the Python pub/sub library and APIs and an API key if you haven't already performed these steps in the thermostat example code.

    sudo pip install --upgrade google-cloud-pubsub
    sudo pip install google-api-python-client google-auth-httplib2 google-auth google-cloud

[Create an API key and service account named api-tester](https://cloud.google.com/iot/docs/samples/end-to-end-sample#create_your_credentials) and make a service_account.json file (steps 1 and 2 in the link) and put it in this example's directory (scp or rsync over ssh are easy ways to move files to your ssh connected Pi if you've downloaded the json file on a host machine). Set the an environment variable to point to this json file:

    export GOOGLE_APPLICATION_CREDENTIALS=service_account.json

Make sure you're authenticated. If you haven't already associated a gcloud project_id with this project, you'll be asked to do so. Use the project you created in the top level readme of this code base.

    gcloud auth application-default login

Change to the directory you've cloned this example to. i.e. "cd ~/Cloud-IoT-Core-Kit-Examples/joystick" and make sure to copy your rsa_private and ec_private files in to this directory or point the scripts to wherever they are.

Our pubsub server relays the servo position to one or many devices:

    python server_relay.py \
     --project_id=$project \
     --pubsub_topic=$mytopic \
     --pubsub_subscription=$mysub \
     --api_key=$apiKey \
     --service_account_json=/path_to_the_file/service_account.json

This client will read the joystick position and send it to the server:

    python pubsub_stick.py \
      --project_id=$project \
      --registry_id=$registry \
      --device_id=$device \
      --private_key_file=/path_to_the_file/rsa_private.pem \
      --algorithm=RS256 \
      --ca_certs=/path_to_the_file/roots.pem

This acknowledgement device will receive the servo position from the server:

    python pubsub_servo.py \
      --project_id=$project \
      --registry_id=$registry \
      --device_id=$device2 \
      --private_key_file=/path_to_the_file/ec_private.pem \
      --algorithm=ES256
