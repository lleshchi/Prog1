import sys
import socket
import argparse

def parser():
    my_parser = argparse.ArgumentParser()

    my_parser.add_argument('Port',
                           metavar='port',
                           type=str,
                           help='the server port number')

    return my_parser.parse_args()


def main():

    args = parser()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # IP address and port number assigned to socket instance
        # The '' means that this server will by reachable by any address this machine has (same as 0.0.0.0)
        server_socket.bind(("0.0.0.0", int(args.Port)))
        # 1 is the backlog size, allows 1 unaccepted connection before it begins to refuse new connections
        server_socket.listen(1)

        while True:

            # conn_socket is new socket object. Use it to send data to client
            # addr is the address on the other side of the connection
            conn_socket, addr = server_socket.accept()
            try:
                recv_message = conn_socket.recv(1024).decode()
                recv_list = recv_message.split()
                method = recv_list[0]
                path = recv_list[1]
                if method == "GET":
                    try:
                        path = "." + path
                        file = open(path, "rb")
                        msg = "HTTP/1.1 200 OK\r\n"
                        conn_socket.send(msg.encode())
                        msg = "Content-Type: text/html\r\n"
                        conn_socket.send(msg.encode())
                        conn_socket.send(file.read())
                        file.close()

                    except FileNotFoundError:
                        msg = "404 Not Found\r\n"
                        conn_socket.send(msg.encode())

                    print("\nClosing Connection Socket\n")
                    conn_socket.close()
                if method == "PUT":

                    print(path)
                    file = open(r"tmp" + path, "wb")
                    data = conn_socket.recv(2048)
                    file.write(data)
                    file.close()
                    msg = "200 OK File Created\r\n"
                    conn_socket.send(msg.encode())

                    print("\nClosing Connection Socket\n")
                    conn_socket.close()

            except KeyboardInterrupt as e:
                print("\nClosing Connection Socket\n")
                conn_socket.close()
                raise e

    except KeyboardInterrupt:
        print("\nClosing Server Socket\n")
        server_socket.close()
        exit()


if __name__ == "__main__":
    main()