__author__ = 'Yair'
########################################
# Name: Yair
# Version: 1.0
# Windows Tested Versions: Win 7 32-bit
# Python Tested Versions: 2.7 32-bit
# Python Environment  :  PyCharm
########################################

import socket
import threading
import os
import ConfigParser
import ssl
from Crypto.Cipher import AES
import YairHTTPRedirectorToHTTPS

protected_folder_directory_name = 'ProtectedFolder'
blacklist_files = ['YairCyberProjectWebsiteServer.py', 'YairHTTPRedirectorToHTTPS.py','config.ini']
post_web_pages=['create_user','retrieve','add_url','retrieve_no_html']
server_port=443
db_server_port=6565
db_server_ip='localhost'
dfs='passmedotteakeay'
iv='The Pass Me IV12'

server_soc = socket.socket()
server_soc = ssl.wrap_socket(server_soc,certfile=protected_folder_directory_name+'/server.pem',server_side=True)
aes=AES.new(dfs,AES.MODE_CFB,iv)



def load_configuration_from_file():
    global server_port
    global db_server_port
    global db_server_ip

    print 'Loading configuration file...'
    try:
        config=ConfigParser.ConfigParser()
        config.read('config.ini')
        server_port=int(config.get('server-options','server-port'))
        db_server_port=int(config.get('server-options','db-server-port'))
        db_server_ip=config.get('server-options','db-server-ip')
        print 'Finished loading configuration file.'

    except (ConfigParser.Error,ValueError):
        print 'Error loading configuration file!'


def reset_aes_obj():
    global aes
    aes = AES.new(dfs,AES.MODE_CFB,iv)


def send_client_communication_to_db_server(client_msg):
    global db_server_obj
    db_server_obj=socket.socket()
    db_server_obj.connect((db_server_ip,db_server_port))
    reset_aes_obj()
    db_server_obj.send(aes.encrypt(client_msg))
    reset_aes_obj()
    db_server_response = aes.decrypt(db_server_obj.recv(1024))
    db_server_obj.close()
    return db_server_response

def initialize_server():
    load_configuration_from_file()
    server_soc.bind(("0.0.0.0", server_port))
    server_soc.listen(5)
    print('Server is running...\n\n----------')


def listen_for_clients():
    while True:
        try:
            client_soc, client_addr = server_soc.accept()
            client_soc.settimeout(3)
            print('Got Connection from:' + client_addr.__str__())
            thrd = threading.Thread(target=communicate_with_client, args=(client_soc,))
            thrd.start()
        except (ssl.SSLError,socket.error) as e:
            print 'Client Error: '+str(e)


def communicate_with_client(client_obj):
    try:
        client_request = str(client_obj.recv(1024))
        print client_request
        print '----------'
        try:
            client_command = client_request.split()[0]
        except Exception as e:
            client_obj.close()
            return

        #checking if user request is valid
        client_web_page_request = client_request.split()[1][1::]
        if protected_folder_directory_name in client_web_page_request:
            file_to_send = file('error403.txt', 'rb')
            client_obj.send(file_to_send.read())
            client_obj.close()
            return
        if client_web_page_request in blacklist_files:
            file_to_send=file('error404.txt','rb')
            client_obj.send(file_to_send.read())
            client_obj.close()
            return
        #handeling the file to return
        if client_command == 'POST':
            if client_web_page_request not in post_web_pages:
                file_to_send=file('error404.txt','rb')
                client_obj.send(file_to_send.read())
                client_obj.close()
                return

            server_response = str(send_client_communication_to_db_server(client_request))
            print server_response
            if client_web_page_request=='create_user':
                if server_response=='Success':
                    file_to_send=file('registersuccess.html','rb')
                else:
                    file_to_send=file('usernameinuse.html','rb')
                client_obj.send(file_to_send.read())
                client_obj.close()
                return
            elif client_web_page_request=='retrieve':
                #inserting server response using string formatting
                #server response start with $ for cannot retrieve # for no passwords ^ for success
                if server_response[0]=='$' or server_response[0]=='#':
                    server_response=server_response[1::]
                    file_to_send=file('error_with_msg.html','rb')
                    html_text_to_send=file_to_send.read().format(msg=server_response)
                    client_obj.send(html_text_to_send)
                    client_obj.close()
                    return
                else:
                    server_response=server_response[1::]
                    file_to_send=file('password_page.html','rb')
                    html_text_to_send=file_to_send.read().format(username=server_response.split()[0],password=server_response.split()[1])
                    client_obj.send(html_text_to_send)
                    client_obj.close()
                    return
            elif client_web_page_request=='retrieve_no_html':
                client_obj.send(server_response)
                client_obj.close()
                return
            elif client_web_page_request=='add_url':
                if server_response=='Changes saved!!!':
                    file_to_send=file('registersuccess.html','rb')
                else:
                    file_to_send=file('usernameinuse.html','rb')
                client_obj.send(file_to_send.read())
                client_obj.close()
                return
            elif client_web_page_request=='retrieve_no_html':
                server_response=server_response[1::]
                client_obj.send(server_response)
                client_obj.close()
                return

        if client_command == 'GET':
            if client_web_page_request == '':
                file_to_send = file('index.html', 'rb')
            else:
                if os.path.isfile(client_web_page_request):
                    file_to_send = file(client_web_page_request, 'rb')
                else:
                    file_to_send = file('error404.txt', 'rb')

        client_obj.send(file_to_send.read())
        client_obj.close()
        file_to_send.close()
        return
    except Exception as e:
        client_obj.send('Sorry!\nThere was an error in our servers...')
        print 'there was an error in communication with client\n' + str(e)
        pass
    client_obj.close()


def setup_http_redirector():
    http_redirector = YairHTTPRedirectorToHTTPS.HTTPRedirector(80)
    http_redirector.initialize_server()
    http_redirector.listen_for_clients()


if __name__ == "__main__":
    thread=threading.Thread(target=setup_http_redirector)
    thread.start()
    initialize_server()
    listen_for_clients()
    server_soc.close()
    print("Done,sent msg to server!")

