__author__ = 'Yair'
import socket
import threading


class HTTPRedirector():
    def __init__(self, server_port=80, url_to_redirect_to='https://127.0.0.1/'):
        self.server_soc = socket.socket()
        self.server_port = server_port
        self.url_to_redirect_to = url_to_redirect_to
        self.log = ''

    def initialize_server(self):
        self.server_soc.bind(("0.0.0.0", self.server_port))
        self.server_soc.listen(5)
        self.log = self.log + '\nServer is running...\n\n----------'

    def listen_for_clients(self):
        while True:
            try:
                client_soc, client_address = self.server_soc.accept()
                client_soc.settimeout(3)
                self.log = self.log + '\nGot Connection from:' + client_address.__str__()
                thread = threading.Thread(target=self.communicate_with_client, args=(client_soc,))
                thread.start()
            except socket.error as e:
                self.log = self.log + '\nClient Error: ' + str(e)

        self.server_soc.close()

    def get_communication_log(self):
        return str(self.log)

    def communicate_with_client(self, client_obj):
        try:
            client_obj.send('''HTTP/1.1 303 See Other\nLocation: {0}\n\n'''.format(self.url_to_redirect_to))
            client_obj.close()
        except Exception as e:
            client_obj.send('Sorry!\nThere was an error in our servers...\n\n')
            client_obj.close()
            self.log = self.log + '\nThere was an error in communication with client\n' + str(e)
