import ruamel.yaml as yaml
import threading
import ray
from flask import Flask, jsonify, Response
import bson
import ray

app = Flask(__name__)

class Config:
    _instance = None
    _config = None
    _lock = threading.Lock()  # Create a lock for thread safety

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:  # Acquire the lock before creating an instance
                if cls._instance is None:
                    cls._instance = super(Config, cls).__new__(cls)
                    cls._instance.load_config()
        return cls._instance

    def load_config(self):
        try:
            with open('/data/config.yml') as config_file:
                self._config = yaml.safe_load(config_file)
        except FileNotFoundError as e:
            return Response(f"The Config file not found: {e.with_traceback()}", status=404, content_type='text/plain')
        except Exception as e:
           return Response(f"Error while loading the config file: {e.with_traceback}", status=500, content_type='text/plain') 
        finally:
            config_file.close()

    @ray.remote
    def get_config(self):
        serialized_data = None
        with self._lock:  # Acquire the lock before loading the config
            if self._config is None:
                self.load_config()
            # Serialize the config data to BSON
            serialized_data = bson.dumps(self._config)
        return serialized_data

#ray.init(address="auto")  # Use "auto" to automatically detect the Ray cluster address

@app.route('/get_config', methods=['GET'])
def get_config():
    config_instance = Config()
    config_data = config_instance.get_config()
    if config_data is None:
        return Response("The config object could not be loaded", status=404, content_type='text/plain')
    else:
        return Response(config_data, content_type='application/bson')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8421)

 