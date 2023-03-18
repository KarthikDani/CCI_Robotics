import socket
import time
import errno

IDENTIFICATION_PORTS = [5005, 5006, 5007]


############## EXPORTED FUNCTIONS ##############

def find_online_users():

  users_query_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  users_query_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  users_query_socket.setblocking(False)
  broadcast_address = '255.255.255.255'

  command = 'status'
  encoded_command = command.encode()

  for identification_port in IDENTIFICATION_PORTS:
      # to all ports that may have identification set up
    identification_endpoint = (broadcast_address, identification_port)
    users_query_socket.sendto(encoded_command, identification_endpoint)

  waiting_time = 1 # seconds to wait for responses
  time.sleep(waiting_time) # wait 

  users = []
  # read all responses
  while True:
    try:
      max_data_size = 1000
      payload, client_endpoint = users_query_socket.recvfrom(max_data_size)
      data = payload.decode()
      username = data[1:]
      status = 'in lobby' if data[0] == '1' else 'waiting for connection' if data[0] == '2'  else 'in game'
      ip_address = client_endpoint[0]

      # add user to list
      user = { 'username': username, 'ip_address': ip_address, 'status': status }
      users.append(user)

    except socket.error as e:
      if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
          # all respones have been read
        break
  
  return users