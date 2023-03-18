import socket
import time
import errno
import threading

IDENTIFICATION_PORTS = [5005, 5006, 5007]
# clients broadcast to this port to identify users on the network

class Controller_token:

  INACTIVE = -1
  STOP = -2
  IN_LOBBY = 1
  WAITING = 2
  IN_GAME = 3


  def __init__(self):
    self.status = self.INACTIVE
  def enable(self):
    self.status = self.IN_LOBBY
  def lobby(self):
    self.status = self.IN_LOBBY
  def game(self):
    self.status = self.IN_GAME
  def disable(self):
    self.status = self.INACTIVE
  def stop(self):
    self.status = self.STOP
  def waiting(self):
    self.status = self.WAITING
# for controlling identification

# identification thread's job
def _start_identification(username, identification_controller):
  identification_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  server_address = ''
  for identification_port in IDENTIFICATION_PORTS:
    try:
      identification_endpoint = (server_address, identification_port)
      identification_socket.bind(identification_endpoint)
    except:
      if identification_port == IDENTIFICATION_PORTS[-1]:
        raise RuntimeError('Bind to identification port failed.')
      continue
    # print('Identification bound to port:', identification_port)
    break

  identification_socket.setblocking(False)

  while True:

    status = identification_controller.status

    while status == identification_controller.INACTIVE:
      time.sleep(0.1)
      status = identification_controller.status
    
    if status == identification_controller.STOP:
      break

    try:
      max_data_size = 1000
      payload, client_endpoint = identification_socket.recvfrom(max_data_size)

    except socket.error as e:
      if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
        time.sleep(0.1)
        continue

    command = payload.decode()
    if command == 'identify':
        # they are querying our username
      encoded_username = username.encode()
      identification_socket.sendto(encoded_username, client_endpoint)
    elif command == 'status':
        # they are querying our status
      data = str(status) + username
      encoded_data = data.encode()
      identification_socket.sendto(encoded_data, client_endpoint)


############## EXPORTED FUNCTIONS ##############

def set_username(username):
  global _identification_controller, _identification_thread
  _identification_controller = Controller_token()
  _identification_thread = threading.Thread(target=_start_identification, args=(username, _identification_controller,))
  _identification_thread.start()

def go_online():
  try:
    _identification_controller
  except:
    raise RuntimeError('set_username() must be called first')
  _identification_controller.enable()

def go_offline():
  try:
    _identification_controller
  except:
    raise RuntimeError('set_username() must be called first')
  _identification_controller.disable()

def in_lobby():
  try:
    _identification_controller
  except:
    raise RuntimeError('set_username() must be called first')
  _identification_controller.lobby()

def in_game():
  try:
    _identification_controller
  except:
    raise RuntimeError('set_username() must be called first')
  _identification_controller.game()

def waiting_for_connection():
  try:
    _identification_controller
  except:
    raise RuntimeError('set_username() must be called first')
  _identification_controller.waiting()


def stop_identification():
  try:
    _identification_controller
  except:
    raise RuntimeError('set_username() must be called first')
  _identification_controller.stop()
  _identification_thread.join()
  _identification_thread = None