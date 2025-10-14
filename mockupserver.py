import os
from flask import Flask

class Server:


    def __init__(self):
        self.app = Flask(__name__)

        @self.app.route("/capacity")
        def capacity():
            return str(1)
        

        @self.app.route("/maxspeed")
        def maxspeed():
            return str(20)
        
        @self.app.route("/<filename>")
        def get_value(filename):
            path = os.path.dirname(os.path.realpath(__file__))
            path = os.path.join(path, "dtd_values", str(filename) + ".txt")
            if os.path.isfile(path):
                with open(path) as f:
                        return f.readline()
            return "file not found", 400
        


def create_app():
    server = Server()
    return server.app