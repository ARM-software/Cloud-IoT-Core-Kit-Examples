## This is a list of useful and example commands for gcloud and the example code in this repository

Shell variables aren't necessary but useful for copy and pasting the following commands without modification. Please set:

    project=my-project-name-1234
    region=us-central1
    registry=example-registry
    device=my-rs256-device
    mysub=my-sub
    events=events


List registries and devices in your $project

    gcloud beta iot registries list --project=$project --region=$region
    gcloud beta iot devices list --project=$project --region=$region --registry=$registry

Create a new registery

    gcloud beta iot registries create $registry \
    --project=$project \
    --region=$region \
    --event-pubsub-topic=projects/$project/topics/events

Create a new device

    gcloud beta iot devices create $device \
    --project=$project \
    --region=$region \
    --registry=$registry \
    --public-key path=rsa_cert.pem,type=rs256

Create a new pubsub subscription to an event

    gcloud beta pubsub subscriptions create projects/$project/subscriptions/$mysub --topic=$events

 Find more at:[ https://cloud.google.com/iot/docs/gcloud_examples](https://cloud.google.com/iot/docs/gcloud_examples)

---
## Sync files on host machine with RasPi as they are changed

    find $IDEdir -type f|entr rsync -aiv --no-o --size-only --progress $IDEdir -e ssh $destPi

---
## Useful RasPi commands for checking your wiring

Blink GPIO 21 (i.e. and LED)

    gpio -g blink 21

Read all of the GPIOs

    gpio readall

See everything on the i2c bus

    i2cdetect -y 1