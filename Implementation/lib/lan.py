import threading, pickle, sys, struct, socket, re

#helper https://stackoverflow.com/a/17668009

def sendmessage(sock, message): #get length od messages
	message = struct.pack('>I', len(message)) + message
	sock.sendall(message)

def recv_msg(sock, block=True):
	raw_messgaelength = recvall(sock, 4, block)
	messgaelength = struct.unpack('>I', raw_messgaelength)[0]
	return recvall(sock, messgaelength, block)

def recvall(sock, num, bl):
    sock.setblocking(bl)
    data = b''

    while len(data) < num:
        pack = sock.recv(num - len(data))
        sock.setblocking(True)
        data += pack
    return data

def findipaddress():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(('10.255.255.255', 1))
        ipaddress = sock.getsockname()[0]
    except:
        ipaddress = '127.0.0.1'
    finally:
        sock.close()
    return ipaddress

def checkipaddress(ipaddress, server):
    sock = socket.socket()
    try:
        value = sock.connect_ex((ipaddress, 11235))
    except socket.error:
        sock.close()
    if value:
        sock.close()
    if value == 0:
        server.append(sock)

def find_server():
    threads = []
    server = []
    ip = findipaddress()
    base = re.match('(\d+\.\d+\.\d+\.)', ip).groups()[0]

    for i in range(0, 256):
        ip = base + str(i)
        threads.append(threading.Thread(target=checkipaddress, args=(ip, server)))
        threads[i].start()

    for i in range(0, 256):
        threads[i].join()
    if server:
        return server[0]
    else:
        return None

def accplayers(server, start, options, lanplayers):
  for i in range(start, options['play_num']):
    server.setblocking(False)

    try:
      client, address = server.accept()
    except BlockingIOError:
      server.setblocking(True)
      return (server, i, options, lanplayers)

    server.setblocking(True)
    lanplayers.append(client)
    name = pickle.loads(recv_msg(client))
    options['names'].append(name)

  return None

def langame(options, queue, bag):
  ownmark = 0
  playmark = 0

  play_num = options['play_num']
  game_online = True
  lanplayers = []

  server = socket.socket()
  server.setblocking(False)

  server.bind(('', 11235))
  server.listen()

  retry = accplayers(server, 1, options, lanplayers)

  while retry:
    if not queue.empty():
      server.close()
      sys.exit()

    retry = accplayers(*retry)

  for m, pl in enumerate(lanplayers):
    sendmessage(pl, pickle.dumps((options, m + 1)))

  players = queue.get()

  for pl in lanplayers:
    sendmessage(pl, pickle.dumps((players, bag)))

  while game_online:
    if playmark != ownmark:
      player = lanplayers[playmark - 1]

      try:
        turn_pack = recv_msg(player, False)
      except BlockingIOError:
        if not queue.empty():
          game_online = queue.get()[-1]

        continue

      turn_pack = pickle.loads(turn_pack)

      if turn_pack and turn_pack[0] != ownmark:
        queue.put(turn_pack)

        game_online = turn_pack[-1]

        for mark, pl in enumerate(lanplayers):
          if mark != playmark - 1:
            sendmessage(pl,pickle.dumps(turn_pack))

        while not queue.empty():
          continue

        playmark = lancurrplayermark(playmark, turn_pack, play_num)
    else:
      if not queue.empty():
        turn_pack = queue.get()
        game_online = turn_pack[-1]

        for pl in lanplayers:
          sendmessage(pl, pickle.dumps(turn_pack))

        playmark = lancurrplayermark(playmark, turn_pack, play_num)

  server.close()

def join_lan_game(options, queue):
  playmark = 0
  game_online = True
  hostipaddress = options.get('ip', None)
  connected = 1

  if hostipaddress:
    server = socket.socket()
    connected = server.connect_ex((hostipaddress, 11235))
  else:
    server = find_server()

  if connected == 0 or server:
    try:
      sendmessage(server, pickle.dumps(options['names'][0]))
    except BrokenPipeError:
      queue.put(False)
    else:
      options, own_mark = pickle.loads(recv_msg(server))
      queue.put((options, own_mark))

      play_num = options['play_num']

      players, bag = pickle.loads(recv_msg(server))
      queue.put((players, bag))

      while not queue.empty():
        continue

      while game_online:
        if own_mark == playmark:
          if not queue.empty():
            turn_pack = queue.get()
            game_online = turn_pack[-1]

            sendmessage(server, pickle.dumps(turn_pack))

            playmark = lancurrplayermark(playmark, turn_pack, play_num)
        else:
          try:
            turn_pack = recv_msg(server, False)
          except BlockingIOError:
            if not queue.empty():
              game_online = queue.get()[-1]
            continue

          turn_pack = pickle.loads(turn_pack)
          game_online = turn_pack[-1]

          if turn_pack[0] != own_mark:
            queue.put(turn_pack)

            playmark = lancurrplayermark(playmark, turn_pack, play_num)

            while not queue.empty():
              continue
    finally:
      server.close()
  else:
    queue.put(False)

def lancurrplayermark(playmark, turn_pack, play_num):
  if len(turn_pack) > 1:
    try:
      chal_check = pickle.loads(turn_pack)[1]
    except:
      chal_check = turn_pack[1]

    # if challenge is unsuccessful
    if type(chal_check) != type(True) or not chal_check:
      return (playmark + 1) % play_num
    else:
      return playmark
  else:
    return playmark