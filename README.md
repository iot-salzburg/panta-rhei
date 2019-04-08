# Digital Twin Stack
### A scalable streaming platform that enables the sharing of IoT data.

This repository is comprised of 3 layers:
* **Digital Twin Messaging Layer** which unifies [Apache Kafka](https://kafka.apache.org/)
 with [SensorThings](http://developers.sensorup.com/docs/) 
* **Digital Twin Client** to easily access the Messaging Layer with only an hand full lines of code
* **Demo Application** to get started as fast as possible 

Example on how to send data using the Digital Twin Client

```python3
from client.digital_twin_client import DigitalTwinClient
config = {"client_name": "demo_app1", "system_name": "demo-system",
          "kafka_bootstrap_servers": "localhost:9092", "gost_servers": "localhost:8082"}
client = DigitalTwinClient(**config)
client = DigitalTwinClient(**config)
client.register(instance_file="digital_twin_mapping/instances")
client.send(quantity="demo_temperature", result=23.4)
```

## Contents

1. [Requirements](#requirements)
2. [Quickstart](#quickstart)
3. [Deploy on a Cluster](#deployment-on-a-cluster)


## Requirements

* Install [Docker](https://www.docker.com/community-edition#/download) version **1.10.0+**
* Install [Docker Compose](https://docs.docker.com/compose/install/) version **1.6.0+**
* Clone this Repository


## Quickstart

This is an instruction on how to set up a demo scenario on your own hardware.
Here, we use Ubuntu 18.04.

 
#### Firstly, **Apache Kafka** and some requirements have to be installed:

The Datastack uses Kafka **version 2.1.0** as the communication layer, the installations is done in `/kafka`.

    sudo apt-get update
    cd setup
    sh kafka/install-kafka-2v1.sh
    sudo sh kafka/install-kafka-libs-2v1.sh
    pip3 install -r requirements.txt

Then, to test the installation:

    /kafka/bin/zookeeper-server-start.sh -daemon /kafka/config/zookeeper.properties
    /kafka/bin/kafka-server-start.sh -daemon /kafka/config/server.properties
    /kafka/bin/kafka-topics.sh --zookeeper localhost:2181 --create --topic test-topic --replication-factor 1 --partitions 1
    /kafka/bin/kafka-topics.sh --zookeeper localhost:2181 --list
    
    /kafka/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic test-topic
    >Hello Franz
    > [Ctrl]+C
    /kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test-topic --from-beginning
    Hello Franz
    
    /kafka/bin/kafka-topics.sh --zookeeper localhost:2181 --create --topic eu.srfg.iot-iot4cps-wp5.car1.data --replication-factor 1 --partitions 1
    /kafka/bin/kafka-topics.sh --zookeeper localhost:2181 --create --topic eu.srfg.iot-iot4cps-wp5.car1.external --replication-factor 1 --partitions 1
    /kafka/bin/kafka-topics.sh --zookeeper localhost:2181 --create --topic eu.srfg.iot-iot4cps-wp5.car1.logging --replication-factor 1 --partitions 1
    Do the same for 'car2' and 'weather-service'


#### Secondly, the **SensorThings Server** GOST is set up to add semantics to Apache Kafka:


    cd setup/gost/
    docker-compose up -d


The flag `-d` stands for `daemon` mode. To check if everything worked well, open
[http://localhost:8082/](http://localhost:8082/) or view the logs:

    docker-compose logs -f


#### Finally, we run the **demo applications** which can be used as starting point:

Now, open new terminals to run the demo applications from the `client` directory:

    python3 demo_applications/car_fleet_1/car_1.py
    > INFO:PR Client Logger:init: Initialising Digital Twin Client with name 'demo_car_1' on 'eu.srfg.iot-iot4cps-wp5.car1'
    ....
    > The air temperature at the demo car 1 is 2.9816131778905497 °C at 2019-03-18T13:54:59.482215+00:00


    python3 demo_applications/car_fleet_2/car_2.py
    > INFO:PR Client Logger:init: Initialising Digital Twin Client with name 'demo_car_2' on 'eu.srfg.iot-iot4cps-wp5.car2'
    ...
    > The air temperature at the demo car 2 is 2.623506013964546 °C at 2019-03-18T12:21:27.177267+00:00
    >   -> Received new external data-point of 2019-03-18T13:54:59.482215+00:00: 'eu.srfg.iot-iot4cps-wp5.car1.car_1.Air Temperature' = 2.9816131778905497 degC.
    

#### Run the Datastore

First, some configs have to be set in order to make the datastore work properly:
    
    ulimit -n 65536  # Increase the max file descriptor
    sudo sysctl -w vm.max_map_count=262144  # Increase the virtual memory
    sudo service docker restart  # Restart docker to make the changes work
    
(further information in progress ...)
    
    
#### Track what happens behind the scenes:

Check the created kafka topics:

    /kafka/bin/kafka-topics.sh --zookeeper localhost:2181 --list
    eu.srfg.iot-iot4cps-wp5.car1.data
    eu.srfg.iot-iot4cps-wp5.car1.external
    eu.srfg.iot-iot4cps-wp5.car1.logging
    eu.srfg.iot-iot4cps-wp5.car2.data
    eu.srfg.iot-iot4cps-wp5.car2.external
    eu.srfg.iot-iot4cps-wp5.car2.logging
    eu.srfg.iot-iot4cps-wp5.weather-service.data
    eu.srfg.iot-iot4cps-wp5.weather-service.external
    eu.srfg.iot-iot4cps-wp5.weather-service.logging
    test-topic

Note that kafka-topics must be created manually as explained in the [Quickstart](#quickstart).

To track the traffic in real time, use the `kafka-consumer-console`: 

    /kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic eu.srfg.iot-iot4cps-wp5.car1.data
    > {"phenomenonTime": "2018-12-04T14:18:11.376306+00:00", "resultTime": "2018-12-04T14:18:11.376503+00:00", "result": 50.05934369894213, "Datastream": {"@iot.id": 2}}

You can use the flag `--from-beginning` to see the whole recordings of the persistence time which are
two weeks by default.
After the tests, stop the services with:

    /kafka/bin/kafka-server-stop.sh 
    /kafka/bin/zookeeper-server-stop.sh 
    cd setup/gost
    docker-compose down

If you want to remove the SensorThings instances from the GOST server, run `docker-compose down -v`.


## Deployment on a Cluster

To deploy Kafka on a local cluster, see the 
[setup/README-Deployment.md](setup/README-Deployment.md) notes.
