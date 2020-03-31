import discord
import main
import prelaunch
import exceptions

############################# Initialising game and client objects
client = discord.Client()
game = main.Game([])
joining_message=None
main_channel_name=None

@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))


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
	global main_channel_name

	# The bot never reacts to its own messages
	if message.author == client.user:
		return

	# Someones wants to know a command
	if message.content == '!help':
		await message.channel.send('Voici toutes les commandes utiles à connaître :\n'
					+'!connected : affiche tous les joueurs actuellement connectés à la partie.\n'
					+'!play : crée une partie.\n'
					+'!start : lance la partie si au moins 4 joueurs sont connectés.\n'
					+'!quit : efface la partie en cours (qu\'elle soit juste créée ou lancée).\n'
					)

	# Someones tries to create a game
	if message.content.startswith('!play'):
		# If a game is already created, then error
		if prelaunch.created():
			await message.channel.send('Une partie est déjà en préparation.')
		else:
			prelaunch.create()
			main_channel_name = str(message.channel)
			joining_message = await message.channel.send('Création d\'une partie de Shadow Hunters.\nPour rejoindre la partie, réagissez simplement à ce message avec un emoji.\nPour quitter la partie avant qu\'elle ne commence, enlevez votre emoji.\nAttention, cet emoji servira à vous repérer durant la partie et ne pourra pas être modifié.')

	# Someones wants to see all players connected
	if message.content.startswith('!connected'):
		# If no game is created, then error
		if (not prelaunch.created()):
			await message.channel.send('Pas de partie en cours.')
		else:
			await message.channel.send(prelaunch.players_list_str())

	# Someone tries to start a game
	if message.content.startswith('!start'):
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
			prelaunch.launch()
			joining_message = None
			await message.channel.send('Le jeu commence maintenant !')
			game = main.Game(prelaunch.players[])

	# Someone tries to shut down the whole game
	if message.content.startswith('!quit'):
		# If no game was created, then error
		if (not prelaunch.created()):
			await message.channel.send('Pas de partie en cours.')
		# If the channel is not the game channel
		elif str(message.channel) != main_channel_name:
			await message.channel.send('Tu dois arrêter la partie dans le canal où elle a été créée.')
		else:
			await message.channel.send('Arrêt de la partie.')
			joining_message = None
			main_channe_name = None
			prelaunch.stop()
			game.clean()

############################# Actually running the bot
client.run('Njk0MjcwODgyMDQ2MDE3NTg4.XoMX_Q.Rmz-5qRP3dzskCrKUzgb-d7TowI')
