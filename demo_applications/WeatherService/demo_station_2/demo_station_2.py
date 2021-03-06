#!/usr/bin/env python3
"""
Demo Setting: Connected Cars
    car1:   The connected car wants to enhance it's safety by retrieving temperature data, to warn the driver on
            approaching slippery road sections. As each car has also temperature data that is of interest for other
            cars, it sends this data to the the platform.
    car2:   The connected car wants to enhance it's safety by retrieving temperature data, to warn the driver on
            approaching slippery road sections. As each car has also temperature data that is of interest for other
            cars, it sends this data to the the platform.
    station1: The weather station is conducted by a local weather service provider which provides the data as a service.
    station2: The weather station is conducted by a local weather service provider which provides the data as a service.
    service_provider: The weather information provider offers temperature data for it's customers.
"""

import os
import sys
import inspect
import time
import pytz
from datetime import datetime

# Append path of client to pythonpath in order to import the client from cli
sys.path.append(os.getcwd())
from client.digital_twin_client import DigitalTwinClient
from demo_applications.simulator.SimulateTemperatures import SimulateTemperatures

# Get dirname from inspect module
filename = inspect.getframeinfo(inspect.currentframe()).filename
dirname = os.path.dirname(os.path.abspath(filename))
INSTANCES = os.path.join(dirname, "instances.json")
MAPPINGS = os.path.join(dirname, "ds-mappings.json")

# Set the configs, create a new Digital Twin Instance and register file structure
# This config is generated when registering a client application on the platform
# Make sure that Kafka and GOST are up and running before starting the platform
config = {"client_name": "weatherstation_2",
          "system": "is.iceland.iot4cps-wp5-WeatherService.Stations",
          "gost_servers": "localhost:8082",
          "kafka_bootstrap_servers": "localhost:9092"}
client = DigitalTwinClient(**config)
# client.register_existing(mappings_file=MAPPINGS)
client.register_new(instance_file=INSTANCES)

randomised_temp = SimulateTemperatures(time_factor=100, day_amplitude=6, year_amplitude=-6, average=3.5)

try:
    while True:
        # epoch and ISO 8601 UTC are both valid
        timestamp = time.time()

        # Measure the demo temperature
        temperature = randomised_temp.get_temp()

        # Send the demo temperature
        client.produce(quantity="temperature", result=temperature, timestamp=timestamp)

        # Print the temperature with the corresponding timestamp in ISO format
        print(f"The air temperature at the demo station 2 is {temperature} °C at "
              f"{datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat()}")

        time.sleep(10)
except KeyboardInterrupt:
    client.disconnect()
