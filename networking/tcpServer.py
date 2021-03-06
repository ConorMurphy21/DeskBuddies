import socketserver
import threading

from networking import packet
from server.serverQueryManager import ServerQueryManager


class TcpHandler(socketserver.BaseRequestHandler):

    manager = None

    def handle(self):
        # self.request is the TCP socket connected to the client
        data = self.request.recv(1024).decode('utf-8')
        query = packet.from_server_str(data)
        response = self.manager.respond(query)
        self.request.sendall(response.encode())


class TcpServer:

    def __init__(self, port):
        self.server = socketserver.TCPServer(('', port), TcpHandler)

    def run(self, sqm: ServerQueryManager):
        TcpHandler.manager = sqm
        threading.Thread(target=self.server.serve_forever).start()




