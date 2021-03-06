import os
import sys

from dotenv import load_dotenv
from flask import Flask

# Import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__name__)), os.pardir)))
from server.create_database import create_tables
from server.views.auth import auth
from server.views.clients import client
from server.views.company import company
from server.views.home import home_bp

# Import application-specific functions
from server.views.kafka_interface import KafkaHandler, KafkaInterface
from server.views.streamhub import streamhub_bp
from server.views.system import system



def create_app():
    # load environment variables automatically from a .env file in the same directory
    load_dotenv()

    # Create Flask app and load configs
    app = Flask(__name__)

    # Register modules as blueprint
    app.register_blueprint(home_bp)
    app.register_blueprint(auth)
    app.register_blueprint(company)
    app.register_blueprint(system)
    app.register_blueprint(client)
    app.register_blueprint(streamhub_bp)

    # app.config.from_object('config')
    app.config.from_envvar('APP_CONFIG_FILE')

    app.logger.setLevel(app.config["LOGLEVEL"])
    app.logger.info("Preparing the platform.")

    if app.config.get("KAFKA_BOOTSTRAP_SERVER"):
        # Create and add a Kafka instance to app. Recreate lost Kafka topics
        app.kafka_interface = KafkaInterface(app)
        # time.sleep(10)
        app.kafka_interface.recreate_lost_topics()
        # Check the connection to Kafka exit if there isn't any
        if not app.kafka_interface.get_connection():
            app.logger.error("The connection to the Kafka Bootstrap Servers couldn't be established.")
            sys.exit(1)

        # Adding a KafkaHandler to the logger, ingests messages into kafka
        kh = KafkaHandler(app)
        app.logger.addHandler(kh)

    app.logger.info("Starting the platform.")

    # Create postgres tables to get the data model
    create_tables(app)
    if app.config.get("KAFKA_BOOTSTRAP_SERVER"):
        app.kafka_interface.create_default_topics()

    # # Test the Kafka Interface by creating and deleting a test topic
    # app.kafka_interface.create_system_topics("test.test.test.test")
    # app.kafka_interface.delete_system_topics("test.test.test.test")

    return app


if __name__ == '__main__':
    # Run application
    app = create_app()
    app.run(debug=app.config["DEBUG"], host="0.0.0.0", port=1908)
