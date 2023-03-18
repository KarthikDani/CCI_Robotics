import socket
import errno
import time
import random

GAME_PORT = 6005
# participating clients must use this port for game communication

board = ''
players = {}
MAX_PLAYERS = 10
MAX_HEALTH = 100
MAX_DAMAGE = 50
LOOT_SPAWN_TIME = 10

def print_current_board():
  print('board:..')

def get_users_move():
  move = input('What is your move: ')
  return move

def update_game_state(player, move):
  global board 
  # update the board
  board = board + move

  print(player + ' played ' + move)

def has_game_ended():
  if (board == 'abcd'):
    return True
  else:
    return False
  
def broadcast(message):
  for player in players.values():
    GAME_PORT.sendto(message.encode(), player['address'])

def spawn_players():
    spawn_points = [(random.randint(0, 100), random.randint(0, 100)) for i in range(MAX_PLAYERS)]
    for i, address in enumerate(players.keys()):
        players[address]['position'] = spawn_points[i]

def spawn_loot():
    global loot
    loot = []
    for i in range(random.randint(5, 10)):
        loot.append({'type': random.choice(['weapon', 'health']), 'position': (random.randint(0, 100), random.randint(0, 100))})
    broadcast("New loot has spawned on the island.")

def check_collisions():
    global loot
    for player in players.values():
        for l in loot:
            if player['position'] == l['position']:
                if l['type'] == 'weapon':
                    player['weapon'] = random.randint(1, 3)
                    broadcast(f"{player['name']} found a weapon.")
                elif l['type'] == 'health':
                    player['health'] = min(MAX_HEALTH, player['health'] + random.randint(20, 40))
                    broadcast(f"{player['name']} found a health pack.")
                loot.remove(l)
            
def deal_damage(attacker, target):
    damage = random.randint(10, MAX_DAMAGE)
    target['health'] = max(0, target['health'] - damage)
    broadcast(f"{attacker['name']} dealt {damage} damage to {target['name']}.")
    if target['health'] == 0:
        broadcast(f"{target['name']} was eliminated by {attacker['name']}.")
        players.pop(target['address'])
        if len(players) == 1:
            winner = list(players.values())[0]
            broadcast(f"{winner['name']} won the game!")
            time.sleep(5)
            players.clear()
            loot.clear()
            spawn_players()
            spawn_loot()



############## EXPORTED FUNCTIONS ##############

def game_server(after_connect):
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as accepter_socket:
      accepter_socket.bind(('', GAME_PORT))
      accepter_socket.listen(1)

      # non-blocking to allow keyboard interupts (^c)
      accepter_socket.setblocking(False)
      while True:
        try:
          game_socket, addr = accepter_socket.accept()
        except socket.error as e:
          if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
            time.sleep(0.1)
            continue
        break

      game_socket.setblocking(True)
      with game_socket:
        after_connect()
        print('Game Started')
        
        while True:

          print("waiting for opp's move")
          opp_move = game_socket.recv(1024).decode()
          if not opp_move:
            break
          update_game_state('opp', opp_move)
          if has_game_ended():
            break

          print_current_board()
          move = get_users_move()
          update_game_state('user', move)
          game_socket.send(move.encode())
          if has_game_ended():
            break

      print_current_board()
      print('Game ended')

def game_client(opponent):
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as game_socket:
      game_socket.connect((opponent, GAME_PORT))
      print('Game Started')

      while True:

        print_current_board()
        move = get_users_move()
        update_game_state('user', move)
        game_socket.send(move.encode())
        if has_game_ended():
          break

        print("waiting for opp's move")
        opp_move = game_socket.recv(1024).decode()
        if not opp_move:
          break
        update_game_state('opp', opp_move)
        if has_game_ended():
          break

  print_current_board()
  print('Game ended')
