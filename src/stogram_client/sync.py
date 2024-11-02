import socket
import json 
import random
import concurrent.futures 
import uuid 

class Client:
    


    def __init__(self, host, port):
        print("Address: {}:{}".format(host,port))


        self.name = str(uuid.uuid4())
        self.host = host
        self.port = port 
        self.sock = None
        self.bytes_sent = 0
        self.bytes_received = 0

    def close(self):
        if self.sock:
            self.sock.close() 
            self.sock = None

    def connect(self):
        if self.sock:
            self.close()
        if not self.sock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host,int(self.port)))
            
            resp = self.call(dict(event="register", subscriber=self.name))
        return self.sock

    def __enter__(self):
        self.connect()
        return self
    
    def publish(self, topic, data):
        return self.call(dict(event="publish", topic=topic, message=data))

    def __exit__(self, *args, **kwargs):
        self.sock.close()
        self.sock = None
        print("Conncetion closed")

    def call(self, obj):
        #self.connect()
        obj_bytes = json.dumps(obj).encode('utf-8')
        self.sock.sendall(obj_bytes)
        self.bytes_sent += len(obj_bytes)
        bytes_ = b''
        while True:
            bytes_ += self.sock.recv(4096)
            resp = bytes_.decode('utf-8')
            try:
                obj = json.loads(resp)
                self.bytes_received += len(resp)
                return obj
            except Exception as ex:
                pass