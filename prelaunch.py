import discord
import exceptions

game_joined=[]
game_created=False
game_launched=False

def nb_players():
	return len(game_joined)

def add(player,emoji):
	global game_joined
	for i in range(0,nb_players()):
		# Comment this block to allow a same player to connect multiple times
		#if game_joined[i][0]==player:
		#	raise exceptions.AlreadyConnected
		if game_joined[i][1]==emoji:
			raise exceptions.EmojiUsed
	if(nb_players() >= 8):
		raise exceptions.GameFull
	game_joined=game_joined+[(player,emoji)]

def delete(player,emoji):
	global game_joined
	found = False
	for i in range(0,nb_players()):
		if (game_joined[i][0]==player) and (game_joined[i][1]==emoji):
			game_joined=game_joined[0:i]+game_joined[i+1:nb_players()]
			found = True
			break
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
			res=res+game_joined[i][0].name+' '+str(game_joined[i][1])+'\n'
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

def create():
	global game_created
	game_created=True

def launch():
	global game_launched
	game_launched=True

def stop():
	global game_created
	global game_launched
	global game_joined
	game_joined = []
	game_created=False
	game_launched=False
