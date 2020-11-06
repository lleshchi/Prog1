import socket
import argparse
import os

def parser():
    my_parser = argparse.ArgumentParser()

    my_parser.add_argument('Port',
                           metavar='port',
                           type=str,
                           help='the server port number')

    return my_parser.parse_args()


def main():
    server_socket = None
    args = parser()
    try:
        # create socket object
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # IP address and port number assigned to socket instance
        # The '' means that this server will by reachable by any address this machine has (same as 0.0.0.0)
        server_socket.bind(('0.0.0.0', int(args.Port)))

        # 1 is the backlog size, allows 1 unaccepted connection before it begins to refuse new connections
        server_socket.listen(1)

        while True:
            conn_socket = None
            try:
                # conn_socket is new socket object. Use it to send data to client
                # addr is the address on the other side of the connection
                conn_socket, addr = server_socket.accept()

                # recv message, max buffer size 1024
                recv_message = conn_socket.recv(1024).decode()

                # split into list words by dividing on whitespace
                # First word will be method, second will be file path
                recv_list = recv_message.split()
                method = recv_list[0]
                path = recv_list[1]

                if method == "GET":
                    try:
                        # Look in current directory (I know I know, there's a better way to do this)
                        # Open file with that name for reading
                        # Send 200 OK confirmation to client (make sure to encode it from string to bytes)
                        path = "." + path
                        file = open(path, "rb")
                        msg = "HTTP/1.1 200 OK\r\n"
                        conn_socket.send(msg.encode())
                        msg = "Content-Type: text/html\r\n"
                        conn_socket.send(msg.encode())

                        # While there is more to read in file, continue reading and sending to client
                        data = file.read()
                        while data:
                            conn_socket.send(data)
                            data = file.read()

                    # If file is not found or directory does not exist, send error message to client
                    except (FileNotFoundError, IsADirectoryError):
                        msg = "HTTP/1.1 404 Not Found\r\n\r\n Sorry, your file request was not found :("
                        conn_socket.send(msg.encode())

                # If put method, create tmp directory, open file that client referred within the tmp directory
                # And read data from socket and write it all to the file while there is more to read
                # Once done with steps above, send 200 OK File Created message (encoded as bytes from string)
                if method == "PUT":
                    print(path)
                    if not os.path.exists("tmp/"):
                        os.makedirs("tmp/")
                    with open("tmp" + path, "wb+") as file:
                        data = conn_socket.recv(4096)
                        while data:
                            file.write(data)
                            data = conn_socket.recv(4096)
                    msg = "200 OK File Created\r\n"
                    conn_socket.send(msg.encode())

            # Make sure to close connection socket (even if exception occurs)
            finally:
                if conn_socket:
                    print("\nClosing Connection Socket\n")
                    conn_socket.close()

    # Exit gracefully on keyboard interrupt
    except KeyboardInterrupt:
        exit()

    # Make sure to close server socket (even if exception occurs)
    finally:
        if server_socket:
            print("\nClosing Server Socket\n")
            server_socket.close()


if __name__ == "__main__":
    main()