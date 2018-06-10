## [Example projects and code](https://github.com/ARM-software/Cloud-IoT-Core-Kit-Examples) are supplied to support the [Arm-based IoT Kit for Cloud IoT Core](https://www.adafruit.com/product/3609) [(kit including RasPi3)](https://www.adafruit.com/product/3594) from [Adafruit](https://www.adafruit.com)
---
# Getting Started

If you purchased the kit that includes the Raspberry Pi 3 Model B, this comes with a pre-formatted NOOBS microSD card. Simply inserting the card into the Pi and powering up the Pi with the included 5v micro USB power supply will boot the Pi and with no interaction, it will default to installing the Raspbian Linux distribution. This is what we want. There are many ways to get a Raspbian and the Pi set up for Google Cloud IoT Core functionality but this guide will focus on getting Raspbian on your WiFi network and headless with secure shell running, gcloud tools installed and IoT Core dependencies for Python installed. These steps will require an HDMI monitor, USB keyboard and mouse.

## Network and firmware updates
1.	Hook up an HDMI monitor, USB keyboard and mouse (plug in an Ethernet cable if you do not intend to use WiFi) then power up your Pi. Once booted, use the WiFi menu in the upper right hand corner of the screen (it should appear with two red 'x's on boot) to connect to the SSID of the wireless network you wish to use. This assumes your network has a DHCP service running on it. If your network has corporate security features, please use another guide appropriate to the type of security required [most require creative use of the wpa_supplicant command and configuration in /etc]. 
2. Use the Raspberry menu to access Preferences->Raspberry Pi Configuration. Under the system tab you can change the hostname to whatever you like and set Boot to CLI (not Desktop); this is optional. Under the Interfaces tab enable "ssh" if you intend to use the Pi without a keyboard and monitor going forward. Under the Localisation tab, set up your Locale, Time Zone and Keyboard preferences. A reboot is required after this.
3. Once rebooted and connected to a network we can secure shell into our Pi remotely or use the command line directly to update our Linux distro and Raspberry Pi 3 firmware. The default uersname is "pi", default password is "raspberry ". To get the Pi's IP, use the command "ifconfig" or nmap your subnet for new ssh services. However you connect, update your Pi with the following commands and change your pi's default password with the "passwd" command if you so choose:

   *Get root access for updates*


    `sudo -s` 

   *This step can take a while due to the number of packages installed by default on the Pi, feel free to uninstall the wolfram-engine, browsers, office applications, etc. at your discretion before running the updates*

    `apt update && apt upgrade && apt dist-upgrade`

    
   *Update the pi firmware (most likely requires a reboot after completion)*

    `rpi-update && reboot`

 *note: you can change most boot, bus and, interface options with a curses interface as well using **sudo raspi-config** i.e. enabling the i2c interface* 

---
## Enabling Cloud IoT Core AP, installing the Google Cloud SDK and registering your first device
Before you proceed please ensure you are logged into Google via your browser with the same userid and password you used with gcloud init on your development machine.

The Google Cloud SDK can be installed on another host machine or the Pi itself. These steps will get the gcloud command installed on the Pi but it can just as easily be done on any machine that you do your development on.

1. Create a Cloud Platform project and enable the Cloud IoT Core API using these **"[Before you begin](https://cloud.google.com/iot/docs/how-tos/getting-started)"** directions.

2. Install **[the latest Google Cloud Tools](https://cloud.google.com/sdk/docs/#deb)** with the included directions. In Linux some of the additions require "sudo gcloud" to be used so you'll need to authorize your root account with sudo in addition to your 'pi' account so instructions from here will diverge from those included [here](https://cloud.google.com/iot/docs/device_manager_guide#install_the_gcloud_cli). Simply follow the directions below instead if you are installing gcloud on the Pi rather than another host machine. SSHing into your Pi (headless) is **strongly** advised in order facilitate authentication of your accounts with your normal desktop browser using copy/paste.


`sudo gcloud components repositories add https://storage.googleapis.com/cloud-iot-gcloud/components-2.json`

3. Create shell variables with your specific project name from step 1 as well as region, registry, device, subscription and event names. Fill in your project ID from step 1, the rest can remain as is below and used in your .profile or .bashrc. i.e.

```bash
project=my-project-name-1234
region=us-central1
registry=example-registry
device=my-rs256-device
device2=my-es256-device
mysub=my-sub
events=events
mytopic=events
```    

4. Create a new registry using the gcloud command. 

```bash
gcloud iot registries create $registry \
	--project=$project \
	--region=$region \
    --event-notification-config=topic=projects/$project/topics/$events
```


5. Create a public/private key pair(s) for your device(s) and create a new device(s) in your project and registry. Or, stretch goal, register one programmatically with [these code samples](https://cloud.google.com/iot/docs/device_manager_samples).

```bash
openssl req -x509 -newkey rsa:2048 -keyout rsa_private.pem -nodes -out rsa_cert.pem
```
```bash
gcloud iot devices create $device \
	--project=$project \
	--region=$region \
	--registry=$registry \
	--public-key path=rsa_cert.pem,type=rs256
```
```bash
openssl ecparam -genkey -name prime256v1 -noout -out ec_private.pem
openssl ec -in ec_private.pem -pubout -out ec_public.pem
```
```bash
gcloud iot devices create $device2 \
	--project=$project \
	--region=$region \
	--registry=$registry \
	--public-key path=ec_public.pem,type=es256
```


6. Create a new pubsub subscription to an event


`gcloud pubsub subscriptions create projects/$project/subscriptions/$mysub --topic=$events`

7. Download the CA root certificates from pki.google.com into the same directory as the example script you want to use:


`wget https://pki.google.com/roots.pem`


---

## Dependencies
Our initial examples for this kit will focus on Python but it is entirely possible to use Ruby, Java, C and other languages to work with Google Cloud IoT. Dependencies include a JSON Web Token and MQTT library as well as a SSL/TLS library like OpenSSL. You'll need the following to run any of the examples included in this repository.

```bash
sudo -s
apt install build-essential libssl-dev libffi-dev python-dev python-pip
pip install pyjwt paho-mqtt cryptography
pip install --upgrade google-api-python-client
pip install --upgrade google-cloud-core
pip install --upgrade google-cloud-pubsub
pip install --upgrade google-auth-httplib2 google-auth oauth2client
exit
```
---

## Hello World - Temperature example

See [CPUTemp example's readme.md](https://github.com/ARM-software/Cloud-IoT-Core-Kit-Examples/tree/master/CPUTemp) to verify your device can communicate with your gcloud project.

---

## PubSub End-to-end - Thermostat example

Wire up the thermostat and led sensors and create an [end to end server and device thermostat system](https://github.com/ARM-software/Cloud-IoT-Core-Kit-Examples/tree/master/pubsub-thermostat).

---

## Joystick End-to-end - analog to digital input/servo control example

Connect a [joystick](https://github.com/ARM-software/Cloud-IoT-Core-Kit-Examples/tree/master/joystick) via 10-bit ADC and use the input to control a PWM servo, e.g. the way a rheostat or app might control multiple lights or a an HVAC controls multiple vents and fans.

---

Find more [samples](https://cloud.google.com/iot/docs/samples/) and [documentation](https://cloud.google.com/iot/docs/) at the Google Cloud Platform IoT site.
