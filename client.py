import sys
import socket
import argparse

class Request:
    def __init__(self, name, port, method, path):
        self.name = name
        self.port = port
        self.method = method
        self.path = path

def parser():
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('Name',
                           metavar='server name',
                           type=str,
                           help='the server name or IP address')
    my_parser.add_argument('Port',
                           metavar='port',
                           type=str,
                           help='the destination port number')
    my_parser.add_argument('Method',
                           metavar='method',
                           type=str,
                           help='GET or PUT')
    my_parser.add_argument('Path',
                           metavar='path',
                           type=str,
                           help='the requested path')

    return my_parser.parse_args()

def main():
    client_socket = None
    file = None
    args = parser()

    if args.Path[0] is not "/":
        args.Path = "/" + args.Path
    my_request = Request(args.Name, int(args.Port), args.Method, args.Path)

    try:
        # socket() call returns socket object with available methods that translate to socket system calls
        # AF_INET refers to the Internet Protocol v4 address family that the socket will communicate with
        # SOCK STREAM defines the socket as a TCP socket. SOCK_DGRAM can be used for UDP
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((my_request.name, my_request.port))

        # GET /index.html HTTP/1.1
        if my_request.method == "GET":
            msg = my_request.method + " " + my_request.path + " " + "HTTP/1.1\r\nHost:" + my_request.name + "\r\n\r\n"
            client_socket.sendall(msg.encode())
            client_socket.shutdown(1)   # Good etiquette, let server know client is done sending but still receiving

        if my_request.method == "PUT":
            msg = my_request.method + " " + my_request.path + "\r\n\r\n"
            client_socket.sendall(msg.encode())
            file = open("." + my_request.path, "rb")
            data = file.read()
            while data:
                client_socket.send(data)
                data = file.read()
            client_socket.shutdown(1)  # Good etiquette, let server know client is done sending but still receiving
            file.close()

        server_response = client_socket.recv(4096)
        while server_response:
            print(server_response.decode() + "\n")
            server_response = client_socket.recv(4096)  # Must be called until no data is left (returns 0 bytes)

    finally:
        if file:
            file.close()
        if client_socket:
            client_socket.close()
            print("\nClosing Client Socket\n")


if __name__ == "__main__":
    main()