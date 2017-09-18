This example requires i2c to be enabled in order to read the temperature sensor. Please run 

    sudo raspi-config

Go to Interface Options->I2C and enable. Exit out of raspi-config and run:

    sudo i2cdetect -F 1

To verify i2c is enabled. 

    sudo i2cdetect -y 1
    sudo i2cdump -y 1 0x77

Will display a grid showing what address any devices are using on the i2C bus. Connect the RasPi Cobbler board to your breadboard and the 40pin cable to your Pi 3. Connect the Temp/Pressure/Humidity Sensor to the breadboard and connect the 3.3v and ground pins to the cobbler. Then connnect the i2c clock and data pins. On the Pi Cobbler SDA is data and SCL is clock. On the BME280 sensor SDI is data and SCK is the clock

    sudo apt-get install build-essential python-pip python-dev python-smbus git
    git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
    cd Adafruit_Python_GPIO
    sudo python setup.py install
    cd ..
    git clone https://github.com/adafruit/Adafruit_Python_BME280.git
    cd Adafruit_Python_BME280
    python Adafruit_BME280_Example.py 
<!-- --or--
    wget https://bitbucket.org/MattHawkinsUK/rpispy-misc/raw/master/python/bme280.py
    python bme280.py -->

You'll also need the Python pub/sub library and APIs

    sudo pip install --upgrade google-cloud-pubsub
    sudo pip install google-api-python-client google-auth-httplib2 google-auth google-cloud

And to [create an API key and service account named api-tester](https://cloud.google.com/iot/docs/device_manager_samples). You'll have to use the API key in the server example.

Set a GOOGLE_APPLICATION_CREDENTIALS environment variable to point to your json file

     export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service_account.json

Make sure you're authenticated

    gcloud auth application-default login


---


python cloudiot_pubsub_example_server.py \
    --project_id=$project \
    --pubsub_topic=$events \
    --pubsub_subscription=$mysub \
    --api_key=$apiKey

python cloudiot_pubsub_example_mqtt_device.py \
      --project_id=$project \
      --registry_id=$registry \
      --device_id=$device \
      --private_key_file=rsa_private.pem \
      --algorithm=RS256