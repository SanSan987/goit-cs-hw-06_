import http.server
import socketserver
import os
import zipfile
import socket
import pymongo
from datetime import datetime

# Підключення до MongoDB
client = pymongo.MongoClient('mongodb+srv://goitlearn:Chchchch1@cluster0.rirxhxh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client["mydatabase"]
collection = db["messages"]

# Розпакування файлів
zip_file_path = 'front-init.zip'
extract_folder = 'front-init'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_folder)

print(f"Files extracted to {os.path.join(os.getcwd(), extract_folder)}")
print(f"Directory content: {os.listdir(extract_folder)}")

# HTTP-сервер
PORT = 3000
class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/front-init/index.html'
        elif self.path == '/message':
            self.path = '/front-init/message.html'
        elif self.path == '/favicon.ico':
            self.path = '/front-init/favicon.ico'
        else:
            self.path = '/front-init' + self.path
        try:
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        except ConnectionAbortedError:
            self.send_error(500, "Connection Aborted Error")
        except Exception as e:
            self.send_error(500, f"Server Error: {str(e)}")
            self.path = '/front-init/error.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/submit':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            post_data = dict(item.split('=') for item in post_data.split('&'))

            username = post_data.get('username')
            message = post_data.get('message')

            # Відправка даних Socket-серверу
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('localhost', 5000))
                data_to_send = f"{username},{message}"
                s.sendall(data_to_send.encode())
                response = s.recv(1024).decode()
                print(f"Received from socket server: {response}")

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Message received")

handler_object = MyHttpRequestHandler

httpd = socketserver.TCPServer(("", PORT), handler_object)
print(f"HTTP server serving at port {PORT}")

# Socket-сервер
def socket_server():
    host = 'localhost'
    port = 5000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print(f"Socket server listening on {host}:{port}")
    while True:
        conn, addr = s.accept()
        print(f"Connection from {addr}")
        data = conn.recv(1024).decode()
        if not data:
            break
        username, message = data.split(',')
        message_doc = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "username": username,
            "message": message
        }
        collection.insert_one(message_doc)
        conn.sendall("Message received".encode())
        conn.close()

import threading

t1 = threading.Thread(target=httpd.serve_forever)
t2 = threading.Thread(target=socket_server)

t1.start()
t2.start()
