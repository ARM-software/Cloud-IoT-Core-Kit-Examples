This example will use the kit's temperature/pressure/humidity sensor to monitor temperature and control a fan in a complete IoT system with both a server and device component. The devices in this system (your Cloud IoT Core kit(s) in this case) publish temperature data on their pubsub registry feeds and individual device IDs. A server python application, which you can run from any machine you like, consumes the telemetry data from your Cloud Pub/Sub topic and events. The server then decides whether to turn on or off the individual devices' fans via a Cloud IoT Core configuration update. 

This example requires i2c to be enabled in order to read the [temperature sensor included with this kit](https://www.adafruit.com/product/2652). Please run 

    sudo raspi-config

Go to Interfacing Options->I2C and enable. Exit out of raspi-config and run:

    sudo i2cdetect -F 1

Connect the RasPi Cobbler board to your breadboard and the 40 pin cable to your Pi 3 [as pictured here](https://cdn-shop.adafruit.com/970x728/2029-01.jpg). The keyed end in the cobbler is obvious, the white striped end of the cable and 90° angle of the cable coming off the RasPi (which is not keyed) are useful visual queues. Connect the Temp/Pressure/Humidity Sensor to the breadboard and connect the 3.3v and ground pins to the cobbler. Then connnect the i2c clock and data pins: On the Pi Cobbler SDA is data pin and SCL is clock pin. On the BME280 sensor SDI is the data pin and SCK is the clock pin.

Verify i2c is enabled. 

    sudo i2cdetect -y 1
    
Will display a grid showing what address any devices are using on the i2C bus. You can dump more information about any of the addresses shown with:
    
    sudo i2cdump -y 1 0x77    <--- hex number shown from previous command
    
Install the Adafruit_Python_GPIO and Adafruit_Python_BME280 abstraction librabies

    sudo apt-get install build-essential python-pip python-dev python-smbus git
    cd ~ && mkdir dev
    cd dev
    git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
    cd Adafruit_Python_GPIO
    sudo python setup.py install
    cd ..
    git clone https://github.com/adafruit/Adafruit_Python_BME280.git
    cd Adafruit_Python_BME280
    sudo python setup.py install
If you wish to sanity check your i2c wiring and sensor further:

    python Adafruit_BME280_Example.py 

Now connect an LED to GIPO 21 and one of the GND pins with a resistor in series on your breadboard. i.e Pin 21 on your Cobbler -> the long pin of the blue LED -> resistor -> GND rail or pin row; [similar to this diagram](https://cdn-learn.adafruit.com/assets/assets/000/024/147/medium800/raspberry_pi_little_cobbler_bb.png). The included 10K resistors will make the LED quite dim. You can sanity check your wiring using the following commands one by one:

    python
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM) 
    GPIO.setup(21, GPIO.OUT)
    GPIO.output(21, GPIO.HIGH)
    GPIO.output(21, GPIO.LOW)
    quit()

Using "GPIO.output(21, GPIO.HIGH)" and "GPIO.output(21, GPIO.LOW)" should toggle your LED on an off.

You'll also need the Python pub/sub library and APIs

    sudo pip install --upgrade google-cloud-pubsub
    sudo pip install google-api-python-client google-auth-httplib2 google-auth google-cloud

[Create an API key and service account named api-tester](https://cloud.google.com/iot/docs/device_manager_samples) and make a service_account.json file (steps 1 and 2 in the link) and put it in this example's directory (scp or rsync over ssh are easy ways to move files to your ssh connected Pi if you've downloaded the json file on a host machine).

Make sure you're authenticated

    gcloud auth application-default login

Change to the directory you've cloned this example to. i.e. "cd ~/Cloud-IoT-Core-Kit-Examples/pubsub-thermostat"
Our control server can run on any host machine, including the RasPi. The "--fan_off" and "--fan_on" arguments are the integer temperatures in °C that will turn on the "fan" LED i.e. when a devices is over 23°C and when it will turn the fan back off i.e. when a device is under 22°C. See optional argument options like "--service_account_json=directory/location" in the code.

    python control_server.py \
     --project_id=$project \
     --pubsub_topic=$events \
     --pubsub_subscription=$mysub \
     --api_key=$apiKey \
     --fan_off=22 \
     --fan_on=23

The client will run on one or many RasPi Cloud IoT kits with unique device ids:

    python pubsub_thermostat.py \
      --project_id=$project \
      --registry_id=$registry \
      --device_id=$device \
      --private_key_file=rsa_private.pem \
      --algorithm=RS256
