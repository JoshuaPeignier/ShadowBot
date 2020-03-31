import discord
import main
import prelaunch
import exceptions
import character_list
import characters
import location

############################# Initialising game and client objects
client = discord.Client()
game = main.Game([])
joining_message=None
turn_message=None
main_channel_name=None
quit_try=False

@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))

############################# Auxiliary functions
def quit_game():
	global game
	global joining_message
	global turn_message
	global main_channel_name
	global quit_try
	quit_try=False
	joining_message = None
	turn_message = None
	main_channel_name = None
	prelaunch.stop()
	game.clean()

def launch_game():
	global game
	global joining_message
	prelaunch.launch()
	joining_message = None
	game = main.Game(prelaunch.players())

############################# How the bots reacts to reactions

@client.event
async def on_reaction_add(reaction,user):

	# When someone reacts to the joining message
	if reaction.message.content.startswith('Création d\'une partie de Shadow Hunters'):
		# Tries to add the user when computing the condition. If already present or emoji already used, sends an error
		nb_players_before = prelaunch.nb_players()
		try:
			prelaunch.add(user,reaction.emoji)
			await reaction.message.channel.send(user.mention+' '+str(reaction.emoji)+' a rejoint la partie.')
			if (nb_players_before == 3) and (prelaunch.nb_players() == 4):
				await reaction.message.channel.send('4 joueurs sont connectés. Vous pouvez commencer la partie avec !start, ou attendre plus de joueurs.')
		except exceptions.AlreadyConnected:
			await reaction.message.channel.send(user.mention+', tu es déjà présent dans la partie.')
		except exceptions.EmojiUsed:
			await reaction.message.channel.send(user.mention+', l\'emoji '+str(reaction.emoji)+' est déjà utilisé.')
		except exceptions.GameFull:
			await reaction.message.channel.send(user.mention+', la partie est déjà complète, tu ne peux pas rejoindre.')

@client.event
async def on_reaction_remove(reaction,user):

	# When someone reacts to the joining message
	if reaction.message.content.startswith('Création d\'une partie de Shadow Hunters'):
		# Tries to delete the user when computing the condition. If not present, nothing happens.
		try:
			prelaunch.delete(user,reaction.emoji)
			await reaction.message.channel.send(user.mention+' '+str(reaction.emoji)+' a quitté la partie.')
		except exceptions.PlayerNotFound:
			print('Exception caught: '+ user.name + ' tried to disconnect, but was not present in the game.')

############################# Main function : How the bots reacts to messages

@client.event
async def on_message(message):
	global game
	global joining_message
	global turn_message
	global main_channel_name
	global quit_try

	# The bot never reacts to its own messages
	if message.author == client.user:
		return

	# Someones wants to see the composition
	if message.content == '!board':
		# If no game is created, then error
		if (not prelaunch.launched()):
			await message.channel.send('Pas de partie en cours.')
		else:
			await message.channel.send(game.get_board())

	# Someones wants to know everything about a character but doesn't know the syntax
	if message.content == '!char':
		await message.channel.send('Syntaxe attendue : !char nom_de_personnage')

	# Someones wants to know everything about a character
	if message.content.startswith('!char '):
		# Retrieve the character_name
		char_name = message.content[6:len(message.content)]
		#res = None
		res = character_list.char_dictionary.get(char_name,None)
		if res == None:
			await message.channel.send('Je ne connais pas de '+char_name+'.')
		else:	
			await message.channel.send(res.info())

	# Someones wants to see the composition
	if message.content == '!compo':
		# If no game is created, then error
		if (not prelaunch.created()):
			await message.channel.send('Pas de partie en cours.')
		else:
			await message.channel.send(prelaunch.composition())

	# Someones wants to see all players connected
	if message.content == '!connected':
		# If no game is created, then error
		if (not prelaunch.created()):
			await message.channel.send('Pas de partie en cours.')
		else:
			await message.channel.send(prelaunch.players_list_str())

	# Someones wants to know a command
	if message.content == '!help':
		await message.channel.send('Voici toutes les commandes utiles à connaître :\n'
					+'**!board** : affiche la position de chaque joueur sur le plateau\n'
					+'**!char** *nom_de_personnage* : vous présente en détails le personnage souhaité.\n'
					+'**!compo** : affiche le nombre de personnages de chaque type pour le nombre de joueurs actuellement connectés.\n'
					+'**!connected** : affiche tous les joueurs actuellement connectés à la partie.\n'

					+'**!location** *nom_de_lieu* : donne les effets du lieu souhaité.\n'
					+'**!order** : affiche l\'ordre des joueurs.\n'
					+'**!play** : crée une partie.\n'
					+'**!players** : affiche les informations (Blessures, Inventaire, Personnage si révélé) de chaque joueur dans l\'ordre du tour.\n'
					+'**!reveal** : révélez votre identité.\n'
					+'**!start** : lance la partie si au moins 4 joueurs sont connectés.\n'
					+'**!quit** : efface la partie en cours (qu\'elle soit juste créée ou lancée).\n'
					)

	# Someones wants to know everything about a location
	if message.content.startswith('!location '):
		# Retrieve the character_name
		loc_name = message.content[10:len(message.content)]
		#res = None
		res = location.location_dictionary.get(loc_name,None)
		if res == None:
			await message.channel.send('Je ne connais pas de '+loc_name+'.')
		else:	
			await message.channel.send(res.getInfo())

	# Someones wants to confirm that the game stops
	if message.content == '!ok':
		if quit_try == True:
			await message.channel.send('Arrêt de la partie.')
			quit_game()

	# No one confirms that the game stops
	if message.content != '!ok':
		if quit_try == True:
			quit_try = False

	# Someones wants to see the order of the players
	if message.content == '!order':
		# If no game is created, then error
		if (not prelaunch.launched()):
			await message.channel.send('Pas de partie en cours.')
		else:
			await message.channel.send(game.players_order_str())

	# Someones tries to create a game
	if message.content == '!play':
		# If a game is already created, then error
		if prelaunch.created():
			await message.channel.send('Une partie est déjà en préparation.')
		else:
			prelaunch.create()
			main_channel_name = str(message.channel)
			joining_message = await message.channel.send('Création d\'une partie de Shadow Hunters.\nPour **rejoindre** la partie, réagissez simplement à ce message avec un emoji.\nPour **quitter** la partie avant qu\'elle ne commence, enlevez votre emoji.\nAttention, cet emoji servira à vous repérer durant la partie et ne pourra pas être modifié.')

	# Someones wants to see the information of all players
	if message.content == '!players':
		# If no game is created, then error
		if (not prelaunch.launched()):
			await message.channel.send('Pas de partie en cours.')
		else:
			await message.channel.send(game.get_players_state())

	# Someones wants to reveal themselves
	if message.content == '!reveal':
		# If no game is created, then error
		if (not prelaunch.launched()):
			await message.channel.send('Pas de partie en cours.')
		else:
			try:
				await message.channel.send(game.reveal_player(message.author))
			except exceptions.PlayerNotFound:
				await message.channel.send(message.author.mention+', tu n\'es pas dans la partie.')
			except exceptions.AlreadyRevealed:
				await message.channel.send(message.author.mention+', ton identité est déjà révélée.')

	# Someone tries to start a game
	if message.content == '!start':
		# If a game is already launched, then error
		if prelaunch.launched():
			await message.channel.send('Une partie a déjà commencé.')
		# If no game was created, then error
		elif (not prelaunch.created()):
			await message.channel.send('Veuillez d\'abord créer une partie en tapant !play')
		# If the channel is not the game channel
		elif str(message.channel) != main_channel_name:
			await message.channel.send('Tu dois lancer la partie dans le canal où elle a été créée.')
		# If not enough players
		elif prelaunch.nb_players() < 4:
			await message.channel.send('Il faut au moins 4 joueurs pour lancer une partie.')
		else:
			await message.channel.send('**Le jeu commence maintenant !**')
			launch_game()
			await message.channel.send(game.players_order_str())
			await message.channel.send(game.get_board())
			for i in range(0,game.nb_players()):
				if game.getChannel(i) == None:
					await game.playerlist[i].getUser().create_dm()
				pChan = game.getChannel(i)
				await pChan.send('Voici ton personnage :\n'+game.playerlist[i].getCharDescription())
			turn_message = await message.channel.send('Tour de '+game.playerlist[0].mention)

	# Someone tries to shut down the whole game
	if message.content == '!quit':
		# If no game was created, then error
		if (not prelaunch.created()):
			await message.channel.send('Pas de partie en cours.')
		# If the channel is not the game channel
		elif str(message.channel) != main_channel_name:
			await message.channel.send('Tu dois arrêter la partie dans le canal où elle a été créée.')
		else:
			quit_try=True
			await message.channel.send('Êtes-vous sûrs de vouloir arrêter la partie ? Tapez !ok pour confirmer.')

############################# Actually running the bot
client.run('Njk0MjcwODgyMDQ2MDE3NTg4.XoMX_Q.Rmz-5qRP3dzskCrKUzgb-d7TowI')
