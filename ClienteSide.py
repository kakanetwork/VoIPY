#!/usr/bin/python

import socket
import os

host = '0.0.0.0'
port = 50005

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((host,port))

server_socket.listen(1)


while True:
        client_socket, client_ip  = server_socket.accept()
        print('Connected by', client_ip)

        lista = ['dovecot', 'named', 'postfix', 'httpd24-httpd', 'sshd']
        services = []

        for i in lista:
            command = "service {0} status".format(i)
            output = os.popen(command).read()
            status = output.replace(".","").split()[-1]
            services.append(status)

        print(services)
        client_socket.sendall(b"{0}".format(services))
        client_socket.close()
