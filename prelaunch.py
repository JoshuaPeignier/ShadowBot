import discord
import exceptions

game_joined=[]
game_created=False
game_launched=False
creator=None

def nb_players():
	return len(game_joined)

def add(player,emoji):
	global game_joined
	if game_launched:
		raise exceptions.GameRunning
	if emoji == '\u27A1' or emoji == '\u274C' or emoji == '\U0001F525' or emoji == '\u2611' or emoji == '\U0001F197' or emoji == '\U0001F6AB' or emoji == '\U0001F3B2' or emoji == '\U0001FA78' or emoji == '\U0001F5E1' or emoji == '\U0001F7E9' or emoji == '\U0001F7EA' or emoji == '\u2B1C' or emoji == '\u2B1B' or emoji == '\U0001F7EB' or emoji == '\U0001F7E7' or emoji == '\U0001F3F9' or emoji == '\U0001FA93' or emoji == '\U0001F52B' or emoji == '\U0001F5E1' or emoji == '\u2694' or emoji == '\U0001F528' or emoji == '\U0001F9AF' or emoji == '\U0001F9BA' or emoji == '\U0001F9ED' or emoji == '\U0001F48D' or emoji == '\u271D' or emoji == '\U0001F4FF' or emoji == '\U0001F4CD' or emoji == '\U0001F5FF' or emoji == '\U0001F6E1' or emoji == '\U0001F489' or emoji == '\U0001F6D1' or emoji == '\u2620':
		raise exceptions.EmojiReserved
	for i in range(0,nb_players()):
		# Comment this block to allow a same player to connect multiple times
		#if game_joined[i][0]==player:
		#	raise exceptions.AlreadyConnected
		if game_joined[i][1]==emoji:
			raise exceptions.EmojiUsed
	if(nb_players() >= 8):
		raise exceptions.GameFull
	game_joined=game_joined+[(player,emoji)]
	print(player.name+' joined with emoji '+str(emoji)+'.')

def delete(player,emoji):
	global game_joined
	if game_launched:
		raise exceptions.GameRunning
	found = False
	for i in range(0,nb_players()):
		if (game_joined[i][0]==player) and (game_joined[i][1]==emoji):
			game_joined=game_joined[0:i]+game_joined[i+1:nb_players()]
			found = True
			break
		elif (game_joined[i][0]==player):
			print('Emoji does not match with player '+str(i))
		elif (game_joined[i][1]==emoji):
			print('Name does not match with player '+str(i))
	if not found:
		raise exceptions.PlayerNotFound

def players():
	return game_joined

def players_list_str():
	if nb_players() == 0:
		return 'Aucun joueur connecté.'
	else:
		res = ''
		for i in range(0,nb_players()):
			res=res+game_joined[i][0].display_name+' '+str(game_joined[i][1])+'\n'
		return res

def composition():
	if nb_players() == 4:
		return "2 Hunters, 2 Shadows"
	elif nb_players() == 5:
		return "2 Hunters, 2 Shadows, 1 Neutre"
	elif nb_players() == 6:
		return "2 Hunters, 2 Shadows, 2 Neutres"
	elif nb_players() == 7:
		return "2 Hunters, 2 Shadows, 3 Neutres"
	elif nb_players() == 8:
		return "3 Hunters, 3 Shadows, 2 Neutres"
	else:
		return "Pas assez de joueurs."

def joined():
	return game_joined

def created():
	return game_created

def launched():
	return game_launched

def create(author):
	global game_created
	global creator
	creator=author
	game_created=True

def launch():
	global game_launched
	game_launched=True

def stop():
	global game_created
	global game_launched
	global game_joined
	global creator
	game_joined = []
	game_created=False
	game_launched=False
	creator=None
