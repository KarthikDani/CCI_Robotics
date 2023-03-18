from src.identification import go_online, go_offline, set_username, stop_identification
from src.identification import in_lobby, in_game, waiting_for_connection
from src.find_users import find_online_users
from src.game import game_server, game_client


def online_users(my_username = None):
  global users
  users = {}

  for i in find_online_users():
    if my_username != None and i['username'] == my_username:
        # ignore own username
      continue
    users[i['username']] = { 'ip_address': i['ip_address'], 'status': i['status'] }

  return users

def main():

  # connecting to the network
  username = input('Enter username: ')
  while username in online_users():
    username = input('Username already taken.\nEnter username: ')
  set_username(username)
  print('Username set to:', username)
  go_online()

    # sample menu program
  while True:

    # print online users
    print('---online users---')
    users = online_users(username)
    for user in users:
      print('{} ({})'.format(user, users[user]['status']))
    if not users:
      print('None Online.')

    # get input
    user_input = input('--MENU--\n(1) Go Online (wait for incoming connections)\n(2) Play against an Online Player\n(3) Refresh\n(4) Exit\n--> ')
    while not user_input.isdigit() and not 1 <= int(user_input) <= 4:
      user_input = input('Invalid input!\nTry again --> ')

    if user_input == '1':
      waiting_for_connection()
      try:
        print('waiting for incoming connection (^c to cancel)')
        game_server(after_connect=in_game)
      except KeyboardInterrupt:
        in_lobby()
        print('cancelled.')
        continue
      in_lobby()
    
    elif user_input == '2':
      try:
        chosen_opponent = input('Enter opponent username (^c to cancel): ')
        while True:
          if chosen_opponent not in users:
            print('No such user online.')
          elif users[chosen_opponent]['status'] != 'waiting for connection':
            print('Opponent not accepting connections.')
          else:
            break
          chosen_opponent = input('Enter opponent username (^c to cancel): ')

      except KeyboardInterrupt:
        print('\ncancelled.')
        continue

      chosen_opponent_ip = users[chosen_opponent]['ip_address']
      in_game()
      game_client(chosen_opponent_ip)
      in_lobby()

    elif user_input == '3':
        # next iteration will print the new online users
      continue
    
    elif user_input == '4':
      break

  go_offline()
  stop_identification()
  print('Program Closed.')
