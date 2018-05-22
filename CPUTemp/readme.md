## CPUTemp Example
---

This example is the our "Hello World" for our Raspberry Pi 3 setup. This should verify that you are able to send JWT encoded messages with MQTT to your Google Cloud project registery topic

 On your Pi export or set $project $registry and $device varialbes to your own and run:

    pi_cpu_temp_mqtt.py --project_id=$project --registry_id=$registry --device_id=$device --private_key_file=rsa_private.pem --algorithm=RS256

gcloud command to fetch CPU temperature:

    gcloud pubsub subscriptions pull --auto-ack projects/$project/subscriptions/$mysub

---
