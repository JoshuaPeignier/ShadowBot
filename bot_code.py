import discord
import main
import prelaunch
import exceptions
import character_list
import characters
import location
import time
import light
import darkness
import vision
import items

class ShadowClient(discord.Client):

	############################# Initialising game and client objects
	game = main.Game([],1)
	prefix='!'
	joining_message=None
	turn_message=None
	board_message=None
	players_message=None
	last_choice_message=None
	buffer_message=[]
	main_channel=None
	quit_try=False
	debug = False
	erasing_messages = False
	future_stored = None
	turn_phase = -1 # -2 : when got a 7 or the compass and blocked in the movement ; -1: AIDS turn and Default value ; 0: beginning, before moving phase ; 1: Moving and applying the effect ; 2: Attacking ; 3: Ending the turn
	quotes_on = True
	version = 1 # 0 : vanilla ; 1 : 2020
	nsa = False
	nsa_user = None

	#@client.event
	async def on_ready(self):
		#current_guild = self.guilds[0]
		#for c in current_guild.channels:
		#	print('The ID of the channel '+c.name+' is '+str(c.id))
		print('We have logged in as {0.user}'.format(self)+' Intents.reactions() is'+str(self.intents.reactions))
		await self.change_presence(activity=discord.Game(name="SH:UCE"))
		character_list.update_version(1)
		light.update_version(1)
		darkness.update_version(1)

	############################# Auxiliary functions
	async def quit_game(self):
		current_message = await self.main_channel.send('Arrêt de la partie.')
		self.quit_try=False
		self.joining_message = None
		self.turn_message = None
		self.board_message = None
		self.players_message = None
		prelaunch.stop()
		self.game.clean()
		self.buffer_message=[]
		await current_message.delete()
		await self.main_channel.send('Partie terminée.')
		self.main_channel = None

	async def launch_game(self):
		prelaunch.launch()
		self.joining_message = None
		self.game = main.Game(prelaunch.players(),self.version)
		await self.main_channel.send('**Préparez-vous.**')
		await self.main_channel.send('Je vous envoie vos personnages par messages privés.')
		for i in range(0,self.game.nb_players()):
			if self.game.getChannel(i) == None:
				await self.game.playerlist[i].getUser().create_dm()
			pChan = self.game.getChannel(i)
			await pChan.send('Voici ton personnage :\n'+self.game.playerlist[i].getCharDescription())
		if self.version == 0:
			await self.main_channel.send('**Version : vanilla**')
		elif self.version == 1:
			await self.main_channel.send('**Version : 2020**')
		await self.main_channel.send('**La partie va commencer dans**')
		await self.count([self.main_channel],5)
		await self.main_channel.send('**La partie commence maintenant !**')
		#await self.main_channel.send(self.game.players_order_str())
		await self.main_channel.send('\_\_\_\_\_\_\_\_\_\_')
		self.players_message = await self.main_channel.send(self.game.get_players_state())
		await self.main_channel.send('\_\_\_\_\_\_\_\_\_\_')
		self.board_message = await self.main_channel.send(self.game.get_board())
		await self.main_channel.send('\_\_\_\_\_\_\_\_\_\_')
		await self.turn_pre(0)

	# Countdown to nb on the given channels
	async def count(self,channel_list,nb):
		for i in range(0,nb):
			for c in channel_list:
				await c.send(nb-i)
			time.sleep(1)

	# Updates the message containing the game state
	async def update(self):
		await self.board_message.edit(content=self.game.get_board())
		await self.players_message.edit(content=self.game.get_players_state())

	# Adds a message to the buffer
	async def add_message_to_buffer(self,message):
		if prelaunch.game_launched:
			self.buffer_message = self.buffer_message + [message]

	# Deletes the messages in the buffer
	async def delete_buffer(self):
		self.erasing_messages = True
		for m in self.buffer_message:
			if m.channel == self.main_channel:
				try:
					await m.delete()
				except discord.NotFound:
					print('Tried to delete a message which was already deleted.\n')
		self.buffer_message = []
		self.erasing_messages = False

	async def victory_message(self):
		await self.main_channel.send('\_\_\_\_\_\_\_\_\_\_')
		await self.main_channel.send('**GAME !!**')
		self.game.game_ended = True
		for i in range(0,self.game.nb_players()):
			if self.game.didPlayerWin(i):
				await self.main_channel.send('> '+self.game.getName(i)+' '+str(self.game.getEmoji(i))+' ('+self.game.playerlist[i].getCharNameColor()+') gagne.')
		self.game.reveal_all()
		await self.update()
		await self.main_channel.send('\_\_\_\_\_\_\_\_\_\_')
		await self.quit_game()

	# Test victory and deaths and then launches the future
	async def victory_and_deaths(self,future):
		self.game.future_after_pillage = None

		# Testing if someone won
		if self.game.didSomeoneWin():
			await self.victory_message()
		else:
			ret_str = self.game.postDeathEffects(self.quotes_on)
			if ret_str != '':
				ret_message = await self.main_channel.send(ret_str)
				await self.add_message_to_buffer(ret_message)

			if self.game.daniel_allegiance == 'Choice' and self.version != 0:
				ret_message = await self.main_channel.send(self.game.getName(self.game.daniel_id)+' '+str(self.game.getEmoji(self.game.daniel_id))+' doit choisir de jouer avec les Hunters :blue_circle: ou les Shadows :red_circle:')
				await self.add_message_to_buffer(ret_message)			
				self.last_choice_message = await self.main_channel.send('Avec qui souhaites-tu jouer ?')
				await self.last_choice_message.add_reaction('\U0001F535')
				await self.last_choice_message.add_reaction('\U0001F534')

				self.future_stored = future

			# If player is alive, proceed to attack phase
			elif self.game.isAlive(self.game.turn_of):
				await future()	
			# Else end the turn
			else:
				await self.turn_post()

	# Pillage and al.
	async def pillage_victory_and_deaths(self,future):
		if self.game.isAlive(self.game.turn_of):
			if self.game.hasItem(self.game.turn_of,items.cross) or (self.version == 0 and self.game.getCharacter(self.game.turn_of) == character_list.bob and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of)):
				for k in range(0,len(self.game.just_died)):
					j = self.game.just_died[k]
					pillage_str = self.game.stealInventory(self.game.turn_of,j)
					if len(pillage_str) > 0:
						ret_message = await self.main_channel.send(pillage_str)
						await self.add_message_to_buffer(ret_message)
				await self.victory_and_deaths(future)
			else:
				for k in range(0,len(self.game.just_died)):
					j = self.game.just_died[k]
					if (len(self.game.lightInventory(j)) + len(self.game.darknessInventory(j)) > 0):
						self.game.waiting_for_pillage = self.game.waiting_for_pillage+[j]	

				if self.game.waiting_for_pillage == []:
					await self.victory_and_deaths(future)
				else:
					self.game.future_after_pillage = future
					await self.pillage()
		else:
			await self.victory_and_deaths(future)

	async def pillage(self):
		if self.game.waiting_for_pillage == []:
			await self.victory_and_deaths(self.game.future_after_pillage)
		else:
			gear_str = ''
			i = self.game.waiting_for_pillage[0]
			if (not self.game.isInventoryEmpty(i)):
				for j in range(0,len(self.game.lightInventory(i))):
					gear_str = gear_str+'> Voler '+(self.game.lightInventory(i))[j].getArticleNameEmoji()+' à '+self.game.getName(i)+' '+str(self.game.getEmoji(i))+'\n'
				for j in range(0,len(self.game.darknessInventory(i))):
					gear_str = gear_str+'> Voler '+(self.game.darknessInventory(i))[j].getArticleNameEmoji()+' à '+self.game.getName(i)+' '+str(self.game.getEmoji(i))+'\n'

			self.last_choice_message = await self.main_channel.send('Tu as tué '+self.game.getName(i)+' '+str(self.game.getEmoji(i))+' et tu dois lui **voler un équipement**. Que souhaites-tu prendre ?\n'+gear_str)

			if (not self.game.isInventoryEmpty(i)):
				for j in range(0,len(self.game.lightInventory(i))):
					await self.last_choice_message.add_reaction((self.game.lightInventory(i))[j].getEmoji())
				for j in range(0,len(self.game.darknessInventory(i))):
					await self.last_choice_message.add_reaction((self.game.darknessInventory(i))[j].getEmoji())

	############################## Functions realising game turns

	# Prepares the turn of the next player
	async def next_turn(self):
		if self.game.playerlist[self.game.turn_of].turns_left > 0:
			self.game.playerlist[self.game.turn_of].turns_left = self.game.playerlist[self.game.turn_of].turns_left-1
			await self.turn_pre(self.game.turn_of)
		else:
			await self.turn_pre((self.game.turn_of+1)%self.game.nb_players())

	# Message of turn-beginning
	async def turn_pre(self,i):
		self.game.turn_of = i
		if self.game.hasGuardianAngel(i):
			current_message = await self.main_channel.send('L\'Ange gardien est défaussé.\n')
			await self.add_message_to_buffer(current_message)
			self.game.loseGuardianAngel(i)
			self.game.discard_light(light.guardian_angel_card)
		if self.game.hasGregorShield(i):
			current_message = await self.main_channel.send('Le Bouclier Fantôme se dissipe.\n')
			await self.add_message_to_buffer(current_message)
			self.game.loseGregorShield(i)
		if self.game.isAlive(i):
			await self.update()
			self.turn_phase = 0
			current_message = await self.main_channel.send('**Tour de '+self.game.getMention(i)+'** '+str(self.game.getEmoji(i))+'.\n')
			await self.add_message_to_buffer(current_message)


			if (self.game.hasItem(self.game.turn_of,items.aids)):
				self.turn_phase = -1
				ret_str = 'Tu dois **lancer un dé** \U0001F3B2 pour appliquer l\'effet de l\'Idole \U0001F5FF'
				self.last_choice_message = await self.main_channel.send(ret_str)
				await self.last_choice_message.add_reaction('\U0001F3B2')
			elif (self.game.erik_active and self.game.getCharacter(self.game.turn_of) == character_list.erik):
				target_str = self.game.print_targets(True,8)
				self.last_choice_message = await self.main_channel.send('Tu peux choisir une des actions suivantes :\n'
					+'> Te soigner **3** Blessures \U0001F489\n'
					+'> Désigner **jusqu\'à 3 joueurs** de ton secteur et leur soigner **2** Blessures.\n'
					+' Voici les joueurs présents sur ton secteur :\n'
					+target_str
					+'> Valider pour soigner **moins de 3** joueurs \U0001F6D1')
				await self.last_choice_message.add_reaction('\U0001F489')
				await self.game.print_target_reactions(self.last_choice_message,True,3)
				await self.last_choice_message.add_reaction('\U0001F6D1')
			elif (self.game.getSleepTime(self.game.turn_of) > 0):
				current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' dort et passe son tour.\n')
				await self.add_message_to_buffer(current_message)
				await self.turn_post()
			else:
				await self.moving_pre()

		else:
			await self.next_turn()

	# Erik finishing with his power
	async def erik_post(self):
		self.game.erik_target_1 = None
		self.game.erik_target_2 = None
		self.game.erik_target_3 = None
		if not self.game.erik_active:
			self.game.erik_active = True
			await self.moving_pre()
		else:
			self.game.erik_active = False
			if (self.game.getSleepTime(self.game.turn_of) > 0):
				current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' dort et passe son tour.\n')
				await self.add_message_to_buffer(current_message)
				await self.turn_post()
			else:
				await self.moving_pre()

	# Asking the player to move
	async def moving_pre(self):
		self.turn_phase = 0
		if self.game.getCharacter(self.game.turn_of) == character_list.catherine and self.game.isAlive(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of) and self.game.isRevealed(self.game.turn_of):
			heal_str = self.game.heal(self.game.turn_of,self.game.turn_of,1,8)
			current_message = await self.main_channel.send(heal_str)
			await self.add_message_to_buffer(current_message)

		await self.update()

		ret_str = '**Clique sur un emoji** pour effectuer une action, '+self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+'.'+' Voici les possibilités : \n'

		if self.game.hasItem(self.game.turn_of,items.compass):
			ret_str = ret_str+'> \U0001F9ED : **2 jets de déplacement** et choix du résultat\n'
		else:
			ret_str = ret_str+'> \U0001F3B2 : **jet de déplacement**\n'
			if self.game.getCharacter(self.game.turn_of) == character_list.link and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of):
				ret_str = ret_str+'> \U0001F4A3 : **2 jets de déplacement** et choix du résultat'
				if self.game.hasItem(self.game.turn_of,items.robe):
					ret_str = ret_str + ' (0 Blessure)\n'
				else:
					ret_str = ret_str + ' (1 Blessure)\n'

		# If the player has a power which it can trigger on its own in the beginning of the turn
		if self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of) and (self.game.getCharacter(self.game.turn_of) == character_list.georges or self.game.getCharacter(self.game.turn_of) == character_list.franklin or self.game.getCharacter(self.game.turn_of) == character_list.fuka or self.game.getCharacter(self.game.turn_of) == character_list.ellen or self.game.getCharacter(self.game.turn_of) == character_list.erik  or self.game.getCharacter(self.game.turn_of) == character_list.majora or self.game.getCharacter(self.game.turn_of) == character_list.agnes or self.game.getCharacter(self.game.turn_of) == character_list.angus):
			ret_str = ret_str+'> Taper **'+self.prefix+'pow** : utiliser ton pouvoir (puis te déplacer)'

		# If he's Emi and revealed, suggest two reactions for the corresponding moves possible
		if self.game.getCharacter(self.game.turn_of) == character_list.emi and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of):
			id_of_player_loc = self.game.getLocationId(self.game.getLocation(self.game.turn_of))
			id_of_twin_loc = self.game.getIdOfTwinLocation(id_of_player_loc)
			id_of_nearby_loc = self.game.getIdOfOtherNearbyLocation(id_of_player_loc)

			color1 = self.game.gamemap[id_of_twin_loc].getColor()
			color2 = self.game.gamemap[id_of_nearby_loc].getColor()
			ret_str = ret_str + '> '+str(color1)+' Aller sur **'+self.game.gamemap[id_of_twin_loc].getNameArticle()+'**\n'
			ret_str = ret_str + '> '+str(color2)+' Aller sur **'+self.game.gamemap[id_of_nearby_loc].getNameArticle()+'**\n'

		target_str = ''
		# If he's the Mummy and revealed, suggest reactions for players on the Otherworld Door
		if self.game.getCharacter(self.game.turn_of) == character_list.mummy and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of) and self.game.mummy_fired:
			target_str = self.game.print_targets(False,7)

		self.last_choice_message = await self.main_channel.send(ret_str+target_str)

		if self.game.hasItem(self.game.turn_of,items.compass):
			await self.last_choice_message.add_reaction('\U0001F9ED')
		else:
			await self.last_choice_message.add_reaction('\U0001F3B2')
			if self.game.getCharacter(self.game.turn_of) == character_list.link and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of):
				await self.last_choice_message.add_reaction('\U0001F4A3')

		# If he's the Mummy and revealed, suggest reactions for players on the Otherworld Door
		if self.game.getCharacter(self.game.turn_of) == character_list.mummy and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of) and self.game.mummy_fired:
			await self.game.print_target_reactions(self.last_choice_message,False,2)

		# TODO : delete the following choices, which are only there for debugging purposes
		if self.debug:
			await self.last_choice_message.add_reaction('\U0001F7E9')
			await self.last_choice_message.add_reaction('\U0001F7EA')
			await self.last_choice_message.add_reaction('\u2B1C')
			await self.last_choice_message.add_reaction('\u2B1B')
			await self.last_choice_message.add_reaction('\U0001F7EB')
			await self.last_choice_message.add_reaction('\U0001F7E7')

		# If he's Emi and revealed, suggest two reactions for the corresponding moves possible
		if self.game.getCharacter(self.game.turn_of) == character_list.emi and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of):
			id_of_player_loc = self.game.getLocationId(self.game.getLocation(self.game.turn_of))
			id_of_twin_loc = self.game.getIdOfTwinLocation(id_of_player_loc)
			id_of_nearby_loc = self.game.getIdOfOtherNearbyLocation(id_of_player_loc)

			color1 = self.game.gamemap[id_of_twin_loc].getColor()
			color2 = self.game.gamemap[id_of_nearby_loc].getColor()
			await self.last_choice_message.add_reaction(color1)
			await self.last_choice_message.add_reaction(color2)


	# Moving with a normal throw
	async def moving_normal_throw(self):

		# Throwing the dices
		dice_result = abs(self.game.d4()+self.game.d6())
		while (self.game.location_of_result(dice_result) == self.game.getLocation(self.game.turn_of) ):
			dice_result = abs(self.game.d4()+self.game.d6())
		current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))
								    +' a fait '+str(dice_result)+'.')
		await self.add_message_to_buffer(current_message)

		# If not a 7, player moves directly
		if dice_result != 7:
			new_loc_str = self.game.move_player_to(self.game.turn_of,dice_result)
			await self.moving_finish(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' se déplace vers **'+new_loc_str+'**.')

		# If it is a 7, printing choices and awaiting a response
		else:
			# Getting the list of possible locations
			location_string = ''
			for i in range(0,6):
				if self.game.gamemap[i] != self.game.getLocation(self.game.turn_of):
					location_string = location_string+'> '+self.game.gamemap[i].getName()+' '+str(self.game.gamemap[i].getColor())+'\n'

			# Sending the message and reactions
			self.turn_phase = -2
			self.last_choice_message = await self.main_channel.send('Tu as fait 7. Choisis vers quelle zone tu souhaites te déplacer. Voici les choix possibles :\n'+location_string)
			for i in range(0,6):
				if self.game.gamemap[i] != self.game.getLocation(self.game.turn_of):
					await self.last_choice_message.add_reaction(self.game.gamemap[i].getColor())

	# Moving with a normal throw
	async def moving_compass(self):

		# Throwing the dices
		dice_result_1 = abs(self.game.d4()+self.game.d6())
		while (self.game.location_of_result(dice_result_1) == self.game.getLocation(self.game.turn_of) ):
			dice_result_1 = abs(self.game.d4()+self.game.d6())
		dice_result_2 = abs(self.game.d4()+self.game.d6())
		while (self.game.location_of_result(dice_result_2) == self.game.getLocation(self.game.turn_of) ) or (self.game.location_of_result(dice_result_2) == self.game.location_of_result(dice_result_1)):
			dice_result_2 = abs(self.game.d4()+self.game.d6())
		current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))
								    +' a fait '+str(dice_result_1)+' et '+str(dice_result_2)+'.')
		await self.add_message_to_buffer(current_message)

		self.turn_phase = -2



		# If not a 7, player moves directly
		if dice_result_1 != 7 and dice_result_2 != 7:
			loc_1 = self.game.location_of_result(dice_result_1)
			loc_2 = self.game.location_of_result(dice_result_2)

			location_string = ''
			for i in range(0,6):
				if self.game.gamemap[i] == loc_1 or self.game.gamemap[i] == loc_2:
					location_string = location_string+'> '+self.game.gamemap[i].getName()+' '+str(self.game.gamemap[i].getColor())+'\n'

			self.last_choice_message = await self.main_channel.send('Où veux-tu aller ? Voici les choix possibles :\n'+location_string)
			for i in range(0,6):
				if self.game.gamemap[i] == loc_1 or self.game.gamemap[i] == loc_2:
					await self.last_choice_message.add_reaction(self.game.gamemap[i].getColor())

		# If it is a 7, printing choices and awaiting a response
		else:
			# Getting the list of possible locations
			location_string = ''
			for i in range(0,6):
				if self.game.gamemap[i] != self.game.getLocation(self.game.turn_of):
					location_string = location_string+'> '+self.game.gamemap[i].getName()+' '+str(self.game.gamemap[i].getColor())+'\n'

			# Sending the message and reactions
			self.turn_phase = -2
			self.last_choice_message = await self.main_channel.send('Tu as fait 7. Choisis vers quelle zone tu souhaites te déplacer. Voici les choix possibles :\n'+location_string)
			for i in range(0,6):
				if self.game.gamemap[i] != self.game.getLocation(self.game.turn_of):
					await self.last_choice_message.add_reaction(self.game.gamemap[i].getColor())

	# Finishing moving
	async def moving_finish(self,move_string):
		await self.update()
		current_message = await self.main_channel.send(move_string)
		await self.add_message_to_buffer(current_message)
		current_message = await self.main_channel.send('\_\_\_')
		await self.add_message_to_buffer(current_message)
		await self.pillage_victory_and_deaths(self.new_zone)

	# Updates the aura, and suggest applying the zone effect
	async def new_zone(self):
		self.turn_phase = 1
		# TODO : update the aura
		if self.game.getLocation(self.game.turn_of) == location.hermit_lair:
			await self.hermit_lair_trigger()
		elif self.game.getLocation(self.game.turn_of) == location.otherworld_door:
			await self.otherworld_door_trigger()
		elif self.game.getLocation(self.game.turn_of) == location.monastery:
			await self.monastery_trigger()
		elif self.game.getLocation(self.game.turn_of) == location.graveyard:
			await self.graveyard_trigger()
		elif self.game.getLocation(self.game.turn_of) == location.haunted_forest:
			await self.haunted_forest_trigger()
		elif self.game.getLocation(self.game.turn_of) == location.ancient_sanctuary:
			await self.ancient_sanctuary_trigger()
		else:
			await self.attack_pre()

	# Prepares the effect of the monastery
	async def otherworld_door_trigger(self):

		# Preparing the players and the message
		player_str = ''
		for i in range(0,self.game.nb_players()):
			if self.game.isAlive(i):
				player_str = player_str +'> '+self.game.getName(i)+' '+str(self.game.getEmoji(i))+'\n'
		self.last_choice_message = await self.main_channel.send('Tu peux **piocher une carte** de la couleur **de ton choix** si tu le souhaites, ou ne rien faire.\n'
			+'Souhaites-tu :\n'
			+'> Piocher une carte Vision \U0001F7E9\n'
			+'> Piocher une carte Lumière \u2B1C\n'
			+'> Piocher une carte Ténèbres \u2B1B\n'
			+'> Ne rien faire \u274C\n')

		# Preparing the reactions
		await self.last_choice_message.add_reaction('\U0001F7E9')
		await self.last_choice_message.add_reaction('\u2B1C')
		await self.last_choice_message.add_reaction('\u2B1B')
		await self.last_choice_message.add_reaction('\u274C')

	# Prepares the effect of the monastery
	async def hermit_lair_trigger(self):

		# Preparing the players and the message
		player_str = ''
		for i in range(0,self.game.nb_players()):
			if self.game.isAlive(i):
				player_str = player_str +'> '+self.game.getName(i)+' '+str(self.game.getEmoji(i))+'\n'
		self.last_choice_message = await self.main_channel.send('Tu peux **piocher une carte** **Vision** si tu le souhaites, ou ne rien faire.\n'
			+'Souhaites-tu :\n'
			+'> Piocher une carte Vision \U0001F7E9\n'
			+'> Ne rien faire \u274C\n')

		# Preparing the reactions
		await self.last_choice_message.add_reaction('\U0001F7E9')
		await self.last_choice_message.add_reaction('\u274C')

	# Prepares the effect of the monastery
	async def monastery_trigger(self):

		# Preparing the players and the message
		player_str = ''
		for i in range(0,self.game.nb_players()):
			if self.game.isAlive(i):
				player_str = player_str +'> '+self.game.getName(i)+' '+str(self.game.getEmoji(i))+'\n'
		self.last_choice_message = await self.main_channel.send('Tu peux **piocher une carte** **Lumière** si tu le souhaites, ou ne rien faire.\n'
			+'Souhaites-tu :\n'
			+'> Piocher une carte Lumière \u2B1C\n'
			+'> Ne rien faire \u274C\n')

		# Preparing the reactions
		await self.last_choice_message.add_reaction('\u2B1C')
		await self.last_choice_message.add_reaction('\u274C')

	# Prepares the effect of the monastery
	async def graveyard_trigger(self):

		# Preparing the players and the message
		player_str = ''
		for i in range(0,self.game.nb_players()):
			if self.game.isAlive(i):
				player_str = player_str +'> '+self.game.getName(i)+' '+str(self.game.getEmoji(i))+'\n'
		self.last_choice_message = await self.main_channel.send('Tu peux **piocher une carte** **Ténèbres** si tu le souhaites, ou ne rien faire.\n'
			+'Souhaites-tu :\n'
			+'> Piocher une carte Ténèbres \u2B1B\n'
			+'> Ne rien faire \u274C\n')

		# Preparing the reactions
		await self.last_choice_message.add_reaction('\u2B1B')
		await self.last_choice_message.add_reaction('\u274C')

	# Prepares the effect of the haunted forest
	async def haunted_forest_trigger(self):

		# Preparing the players and the message
		player_str = self.game.print_targets(True,4)

		self.last_choice_message = await self.main_channel.send('Choisis **une action** et **un joueur** auquel l\'appliquer **en cliquant sur leurs emojis**. Si tu ne veux rien faire, clique juste sur la croix \u274C\n'
			+'Souhaites-tu :\n'
			+'> Soigner 1 Blessure à un joueur \U0001F489\n'
			+'> Infliger 2 Blessures à un joueur \U0001FA78\n'
			+'> Ne rien faire \u274C\n'
			+'A quel joueur ?\n'+player_str)

		# Preparing the reactions
		await self.last_choice_message.add_reaction('\U0001F489')
		await self.last_choice_message.add_reaction('\U0001FA78')
		await self.last_choice_message.add_reaction('\u274C')
		await self.game.print_target_reactions(self.last_choice_message,True,0)

	# Applies the effect of the haunted forest when victim and effect have been decided
	async def haunted_forest_post(self):
		if self.game.haunted_forest_victim != None and self.game.haunted_forest_effect != 0:
			ret_str = ''
			if self.game.haunted_forest_effect == 1:
				ret_str = self.game.heal(self.game.turn_of,self.game.haunted_forest_victim,1,1)
			elif self.game.haunted_forest_effect == -1:
				ret_str = self.game.damage(self.game.turn_of,self.game.haunted_forest_victim,2,1,self.quotes_on)

			if ret_str != '':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				current_message = await self.main_channel.send(ret_str)
				await self.add_message_to_buffer(current_message)
				self.game.haunted_forest_victim = None
				self.game.haunted_forest_effect = 0

				await self.pillage_victory_and_deaths(self.attack_pre)

	# Prepares the effect of the monastery
	async def ancient_sanctuary_trigger(self):

		if self.game.hasItem(self.game.turn_of,items.ring):
			ret_str = self.game.heal(self.game.turn_of,self.game.turn_of,1,5)
			current_message = await self.main_channel.send(ret_str)
			await self.add_message_to_buffer(current_message)

		if self.game.someoneElseHasItems(self.game.turn_of):
			gear_str = ''
			for i in range(0,self.game.nb_players()):
				if (not self.game.isInventoryEmpty(i)) and i != self.game.turn_of:
					for j in range(0,len(self.game.lightInventory(i))):
						gear_str = gear_str+'> Voler '+(self.game.lightInventory(i))[j].getArticleNameEmoji()+' à '+self.game.getName(i)+' '+str(self.game.getEmoji(i))+'\n'
					for j in range(0,len(self.game.darknessInventory(i))):
						gear_str = gear_str+'> Voler '+(self.game.darknessInventory(i))[j].getArticleNameEmoji()+' à '+self.game.getName(i)+' '+str(self.game.getEmoji(i))+'\n'
			gear_str = gear_str + '> Ne rien voler \u274C'

			self.last_choice_message = await self.main_channel.send('Tu peux **voler un équipement** à un autre joueur. Que souhaites-tu prendre ?\n'+gear_str)

			for i in range(0,self.game.nb_players()):
				if (not self.game.isInventoryEmpty(i)) and i != self.game.turn_of:
					for j in range(0,len(self.game.lightInventory(i))):
						await self.last_choice_message.add_reaction((self.game.lightInventory(i))[j].getEmoji())
					for j in range(0,len(self.game.darknessInventory(i))):
						await self.last_choice_message.add_reaction((self.game.darknessInventory(i))[j].getEmoji())
			await self.last_choice_message.add_reaction('\u274C')
		else:
			current_message = await self.main_channel.send('Il n\'y a rien à voler.')
			await self.add_message_to_buffer(current_message)
	
			await self.area_effect_post()

	# Ends the effect of the previously designated area, when something happened automatically
	async def area_effect_post(self):
		await self.update()
		if self.game.getCharacter(self.game.turn_of) == character_list.bob and (self.game.bob_draw) and (self.game.last_drawn != 0) and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of) and self.version != 0:
			await self.bob_redrawing()
		else:
			self.last_choice_message = await self.main_channel.send('Clique ici pour continuer '
							+self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+'.')
			await self.last_choice_message.add_reaction('\u27A1')

	# Allowing the player to attack if he wants to
	async def attack_pre(self):
		self.turn_phase = 2
		current_message = await self.main_channel.send('\_\_\_')
		await self.add_message_to_buffer(current_message)
		await self.update()
		# if the player is despair, then call a new function
		if self.game.getCharacter(self.game.turn_of) == character_list.despair and self.game.isRevealed(self.game.turn_of):
			await self.attack_pre_despair()
		# if the player has a gunmachine, then call a new function
		elif self.game.hasItem(self.game.turn_of,items.gunmachine):
			await self.attack_pre_gunmachine()
		# else if the player is Mograine, then call a new function to impose him to choose two targets
		elif self.game.getCharacter(self.game.turn_of) == character_list.mograine and self.game.isAbilityAvailable(self.game.turn_of) and self.game.isRevealed(self.game.turn_of) and self.game.isAlive(self.game.turn_of) and self.game.nbPlayersReachable(self.game.turn_of) > 1:
			await self.attack_pre_mograine()
		# else, we call attack_pre_normal
		else:
			await self.attack_pre_normal()

	# Allowing the player to attack if he wants to
	async def attack_pre_normal(self):
		# Getting locations ID
		id_of_player_loc = self.game.getLocationId(self.game.getLocation(self.game.turn_of))
		id_of_twin_loc = self.game.getIdOfTwinLocation(id_of_player_loc)

		# Preparing the message of all possibilities
		targets_string = self.game.print_targets(False,1)

		if (not self.game.hasItem(self.game.turn_of,items.katana)) or (targets_string == ''):
			targets_string = targets_string+'> N\'attaquer personne \u274C'

		# Sending the message
		self.last_choice_message = await self.main_channel.send('**Clique sur un emoji** pour attaquer un joueur, '
					+self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+'.'
					+' Voici les possibilités : \n'+targets_string)	

		await self.game.print_target_reactions(self.last_choice_message,False,1)
		if (not self.game.hasItem(self.game.turn_of,items.katana)) or (targets_string == '> N\'attaquer personne \u274C'):
			await self.last_choice_message.add_reaction('\u274C')

	# Allowing the player to attack with Mograine's Power if he wants to
	async def attack_pre_mograine(self):
		# Getting locations ID
		id_of_player_loc = self.game.getLocationId( self.game.getLocation(self.game.turn_of))
		id_of_twin_loc = self.game.getIdOfTwinLocation(id_of_player_loc)

		# Preparing the message of all possibilities
		targets_string = self.game.print_targets(False,1)

		if (not self.game.hasItem(self.game.turn_of,items.katana)) or (targets_string == ''):
			targets_string = targets_string+'> N\'attaquer personne \u274C'

		# Sending the message
		self.last_choice_message = await self.main_channel.send('**Choisis 2 joueurs** à attaquer (le deuxième ne subira que la moitié des dégâts), '+self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+'.\n'
					+ 'Pour n\'attaquer qu\'un seul joueur, **choisis-le**, puis clique sur le bouton Stop \U0001F6D1.\n'
					+' Voici les possibilités : \n'+targets_string)	

		await self.game.print_target_reactions(self.last_choice_message,False,1)
		await self.last_choice_message.add_reaction('\U0001F6D1')
		if (not self.game.hasItem(self.game.turn_of,items.katana)) or (targets_string == '> N\'attaquer personne \u274C'):
			await self.last_choice_message.add_reaction('\u274C')

	# Allowing Despair to attack if he wants to
	async def attack_pre_despair(self):

		action_string = '> \u2620 : Attaquer\n'
		if (not self.game.hasItem(self.game.turn_of,items.katana)):
			action_string = action_string+'> \u274C : Ne pas attaquer'

		# Sending the message
		self.last_choice_message = await self.main_channel.send('Si tu attaques, tous les joueurs (excepté toi) subiront des dégâts. Que souhaites-tu faire ?\n'+action_string)	

		# Adding reactions
		await self.last_choice_message.add_reaction('\u2620')
		if (not self.game.hasItem(self.game.turn_of,items.katana)):
			await self.last_choice_message.add_reaction('\u274C')

	# Allowing the player to attack with the gunmachine if he wants to
	async def attack_pre_gunmachine(self):
		# Getting locations ID
		id_of_player_loc = self.game.getLocationId(self.game.getLocation(self.game.turn_of))
		id_of_twin_loc = self.game.getIdOfTwinLocation(id_of_player_loc)

		# Preparing the message of all possibilities
		targets_string = self.game.print_targets(False,1)

		action_string = '> \U0001F52B : Attaquer\n'
		if (not self.game.hasItem(self.game.turn_of,items.katana)) or (targets_string == ''):
			action_string = action_string+'> \u274C : Ne pas attaquer'

		# Sending the message
		self.last_choice_message = await self.main_channel.send('Tu as la Mitrailleuse, '+self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' ; si tu choisis d\'attaquer, les joueurs suivants seront touchés :\n'+targets_string+'Que souhaites-tu faire? \n'+action_string)	

		# Adding reactions
		await self.last_choice_message.add_reaction('\U0001F52B')
		if (not self.game.hasItem(self.game.turn_of,items.katana)) or (targets_string == '> \u274C : Ne pas attaquer'):
			await self.last_choice_message.add_reaction('\u274C')

	# Effectively attacking
	async def attack_mid(self,target_id):
		self.game.mograine_target_1 = None
		self.game.mograine_target_2 = None

		# Computing the dice_value
		dice_value = 0
		if (self.game.hasItem(self.game.turn_of,items.katana)):
			dice_value = self.game.d4()
		elif self.game.getCharacter(self.game.turn_of) == character_list.valkyrie and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of):
			dice_value = self.game.d4()
		else:
			dice_value = abs(self.game.d6()-self.game.d4())
		current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' a fait '+str(dice_value)+'.')
		await self.add_message_to_buffer(current_message)

		# Storing former health
		former_health = self.game.playerlist[target_id].wounds
		vampire_heal_str = ''

		# Lothaire can try to block
		if self.game.getCharacter(target_id) == character_list.lothaire and self.game.isRevealed(target_id) and self.game.isAbilityAvailable(target_id):
			block_value = abs(self.game.d6()-self.game.d4())	
			current_message = await self.main_channel.send(self.game.getName(target_id)+' '+str(self.game.getEmoji(target_id))+' a fait '+str(block_value)+'.')
			await self.add_message_to_buffer(current_message)
			if block_value > dice_value+1 and dice_value > 0:
				damage_str = self.game.damage(self.game.turn_of,target_id,dice_value,11,self.quotes_on)
			else:
				damage_str = self.game.damage(self.game.turn_of,target_id,dice_value,0,self.quotes_on)

		else:
			damage_str = self.game.damage(self.game.turn_of,target_id,dice_value,0,self.quotes_on)

		# Computing the real damage inflicted
		new_value = self.game.playerlist[target_id].wounds-former_health

		# Vampire healing if some damage was inflited
		if self.game.getCharacter(self.game.turn_of) == character_list.vampire and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of) and new_value > 0:
			if self.version == 0:
				vampire_heal_str = self.game.heal(self.game.turn_of,self.game.turn_of,2,7)
			elif self.version != 0:
				vampire_heal_str = self.game.heal(self.game.turn_of,self.game.turn_of,1,7)

		# Sending messages
		current_message = await self.main_channel.send(damage_str+vampire_heal_str)
		await self.add_message_to_buffer(current_message)
		await self.pillage_victory_and_deaths(self.counterattack)


	# Effectively attacking with Mograine
	async def attack_mid_mograine(self):
		# Computing the dice_value

		dice_value = 0
		if (self.game.hasItem(self.game.turn_of,items.katana)):
			dice_value = self.game.d4()
		elif self.game.getCharacter(self.game.turn_of) == character_list.valkyrie and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of):
			dice_value = self.game.d4()
		else:
			dice_value = abs(self.game.d6()-self.game.d4())
		current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' a fait '+str(dice_value)+'.')
		await self.add_message_to_buffer(current_message)


		# Lothaire can try to block
		if self.game.getCharacter(self.game.mograine_target_1) == character_list.lothaire and self.game.isRevealed(self.game.mograine_target_1) and self.game.isAbilityAvailable(self.game.mograine_target_1):
			block_value = abs(self.game.d6()-self.game.d4())	
			current_message = await self.main_channel.send(self.game.getName(self.game.mograine_target_1)+' '+str(self.game.getEmoji(self.game.mograine_target_1))+' a fait '+str(block_value)+'.')
			await self.add_message_to_buffer(current_message)
			if block_value > dice_value+1 and dice_value > 0:
				damage_str = self.game.damage(self.game.turn_of,self.game.mograine_target_1,dice_value,11,self.quotes_on)
			else:
				damage_str = self.game.damage(self.game.turn_of,self.game.mograine_target_1,dice_value,0,self.quotes_on)

		else:
			damage_str = self.game.damage(self.game.turn_of,self.game.mograine_target_1,dice_value,0,self.quotes_on)

		# Sending messages
		current_message = await self.main_channel.send(damage_str)
		await self.add_message_to_buffer(current_message)


		# Lothaire can try to block
		if self.game.getCharacter(self.game.mograine_target_2) == character_list.lothaire and self.game.isRevealed(self.game.mograine_target_2) and self.game.isAbilityAvailable(self.game.mograine_target_2):
			block_value = abs(self.game.d6()-self.game.d4())	
			current_message = await self.main_channel.send(self.game.getName(self.game.mograine_target_2)+' '+str(self.game.getEmoji(self.game.mograine_target_2))+' a fait '+str(block_value)+'.')
			await self.add_message_to_buffer(current_message)
			if block_value > dice_value+1 and dice_value > 0:
				damage_str = self.game.damage(self.game.turn_of,self.game.mograine_target_2,dice_value,14,self.quotes_on)
			else:
				damage_str = self.game.damage(self.game.turn_of,self.game.mograine_target_2,dice_value,13,self.quotes_on)

		else:
			damage_str = self.game.damage(self.game.turn_of,self.game.mograine_target_2,dice_value,13,self.quotes_on)

		# Sending messages
		current_message = await self.main_channel.send(damage_str)
		await self.add_message_to_buffer(current_message)


		self.game.mograine_target_1 = None
		self.game.mograine_target_2 = None
		await self.pillage_victory_and_deaths(self.counterattack)


	# Effectively attacking with despair
	async def attack_mid_despair(self):
		# Computing the dice_value
		dice_value = 0
		if (self.game.hasItem(self.game.turn_of,items.katana)):
			dice_value = self.game.d4()
		else:
			dice_value = abs(self.game.d6()-self.game.d4())
		current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' a fait '+str(dice_value)+'.')
		await self.add_message_to_buffer(current_message)

		# Damaging each player
		for i in range(0,self.game.nb_players()):

			# If player is reachable
			if (i != self.game.turn_of) and (self.game.isAlive(i)):
				# Damaging the player


				# Lothaire can try to block
				if self.game.getCharacter(i) == character_list.lothaire and self.game.isRevealed(i) and self.game.isAbilityAvailable(i):
					block_value = abs(self.game.d6()-self.game.d4())	
					current_message = await self.main_channel.send(self.game.getName(i)+' '+str(self.game.getEmoji(i))+' a fait '+str(block_value)+'.')
					await self.add_message_to_buffer(current_message)
					if block_value > dice_value+1 and dice_value > 0:
						damage_str = self.game.damage(self.game.turn_of,i,dice_value,11,self.quotes_on)
					else:
						damage_str = self.game.damage(self.game.turn_of,i,dice_value,0,self.quotes_on)

				else:
					damage_str = self.game.damage(self.game.turn_of,i,dice_value,0,self.quotes_on)

				current_message = await self.main_channel.send(damage_str)
				await self.add_message_to_buffer(current_message)

		await self.pillage_victory_and_deaths(self.counterattack)

	# Effectively attacking with gunmachine
	async def attack_mid_gunmachine(self):
		# Computing the dice_value
		dice_value = 0
		if (self.game.hasItem(self.game.turn_of,items.katana)):
			dice_value = self.game.d4()
		elif self.game.getCharacter(self.game.turn_of) == character_list.valkyrie and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of):
			dice_value = self.game.d4()
		else:
			dice_value = abs(self.game.d6()-self.game.d4())
		current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' a fait '+str(dice_value)+'.')
		await self.add_message_to_buffer(current_message)

		# Getting locations ID
		id_of_player_loc = self.game.getLocationId(self.game.getLocation(self.game.turn_of))
		id_of_twin_loc = self.game.getIdOfTwinLocation(id_of_player_loc)

		vampire_heals = False

		# Damaging each player
		for i in range(0,self.game.nb_players()):
			no_bow_condition = (self.game.getLocation(i) == self.game.gamemap[id_of_player_loc] or self.game.getLocation(i) == self.game.gamemap[id_of_twin_loc]) and not self.game.hasItem(self.game.turn_of,items.bow)
			bow_condition = self.game.getLocation(i) != self.game.gamemap[id_of_player_loc] and self.game.getLocation(i) != self.game.gamemap[id_of_twin_loc] and self.game.hasItem(self.game.turn_of,items.bow)

			# If player is reachable
			if (i != self.game.turn_of) and (self.game.isAlive(i)) and (no_bow_condition or bow_condition):
				# Damaging the player
				former_health = self.game.playerlist[i].wounds
				vampire_heal_str = ''


				# Lothaire can try to block
				if self.game.getCharacter(i) == character_list.lothaire and self.game.isRevealed(i) and self.game.isAbilityAvailable(i):
					block_value = abs(self.game.d6()-self.game.d4())	
					current_message = await self.main_channel.send(self.game.getName(i)+' '+str(self.game.getEmoji(i))+' a fait '+str(block_value)+'.')
					await self.add_message_to_buffer(current_message)
					if block_value > dice_value+1 and dice_value > 0:
						damage_str = self.game.damage(self.game.turn_of,i,dice_value,11,self.quotes_on)
					else:
						damage_str = self.game.damage(self.game.turn_of,i,dice_value,0,self.quotes_on)

				else:
					damage_str = self.game.damage(self.game.turn_of,i,dice_value,0,self.quotes_on)



				# Computing the real damage inflicted, for the heal of the vampire
				new_value = self.game.playerlist[i].wounds-former_health
				if new_value > 0:
					vampire_heals = True

				current_message = await self.main_channel.send(damage_str)
				await self.add_message_to_buffer(current_message)

		# If the vampire damaged at least one player, then heals
		if vampire_heals and self.game.getCharacter(self.game.turn_of) == character_list.vampire and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of):
			vampire_heal_str = self.game.heal(self.game.turn_of,self.game.turn_of,1,7)
			current_message = await self.main_channel.send(vampire_heal_str)
			await self.add_message_to_buffer(current_message)

		await self.pillage_victory_and_deaths(self.counterattack)

	# Werewolf counterattack
	async def counterattack(self):
		if self.game.counterattack_available:
			self.last_choice_message = await self.main_channel.send('Veux-tu contre-attaquer, '+self.game.getMention(self.game.werewolf_id)+' '+str(self.game.getEmoji(self.game.werewolf_id))+' ?\n')
			await self.last_choice_message.add_reaction('\u2611')
			await self.last_choice_message.add_reaction('\u274C')
		else:
			await self.turn_post()

	# Message of turn-end
	async def turn_post(self):
		self.turn_phase = 3
		await self.update()
		power_message_1 = ''
		power_message_2 = ''
		self.game.mummy_fired = True
		if (self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of) and (self.game.getSleepTime(self.game.turn_of) == 0) and ( self.game.getCharacter(self.game.turn_of) == character_list.gregor or self.game.getCharacter(self.game.turn_of) == character_list.varimathras or self.game.getCharacter(self.game.turn_of) == character_list.lich) ):
			power_message_1 = 'Voici tes possibilités :\n'
			power_message_2 = '> Taper **'+self.prefix+'pow** : utiliser ton pouvoir'
		self.last_choice_message = await self.main_channel.send('C\'est la fin de ton tour, '
						+self.game.getMention(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+'.\n'
						+power_message_1
						+'> \u27A1 : Terminer le tour\n'
						+power_message_2)
		await self.last_choice_message.add_reaction('\u27A1')


	############################# Functions dediacted do drawing cards

	async def bob_redrawing(self):
		light_or_dark = ''
		if self.game.last_drawn == 1:
			light_or_dark = 'Lumière'
		elif self.game.last_drawn == 2:
			light_or_dark = 'Ténèbres'

		self.last_choice_message = await self.main_channel.send('Veux-tu piocher une autre carte '+light_or_dark+', '+self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' ?')
		await self.last_choice_message.add_reaction('\u2611')
		await self.last_choice_message.add_reaction('\u274C')		

	# Drawing a light card

	async def draw_light(self):
		card = self.game.draw_one_light()

		current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' pioche '+card.fullName()+'.\n')
		await self.add_message_to_buffer(current_message)

		if card == light.holy_water_card:
			self.game.last_drawn = 1
			self.game.discard_light(card)

			ret_str = self.game.heal(self.game.turn_of,self.game.turn_of,2,2)
			current_message = await self.main_channel.send(ret_str)
			await self.add_message_to_buffer(current_message)

			await self.area_effect_post()

		if card == light.mirror_card:
			self.game.last_drawn = 1
			self.game.discard_light(card)

			current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' doit révéler son identité si c\'est un Shadow :red_circle: (autre que Métamorphe).')
			await self.add_message_to_buffer(current_message)

			if self.game.isShadow(self.game.turn_of) and self.game.playerlist[self.game.turn_of].getCharacter() != character_list.metamorph and (not self.game.isRevealed(self.game.turn_of)):
				ret_str = self.game.playerlist[self.game.turn_of].reveals()
				current_message = await self.main_channel.send(ret_str)
				await self.add_message_to_buffer(current_message)
			elif (not self.game.isRevealed(self.game.turn_of)):
				current_message = await self.main_channel.send('Rien ne se passe.')
				await self.add_message_to_buffer(current_message)

			await self.area_effect_post()

		if card == light.divine_lightning_card:
			self.game.last_drawn = 1
			self.game.discard_light(card)

			current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' inflige **2** Blessures à tous les autres joueurs.')
			await self.add_message_to_buffer(current_message)

			for i in range(0,self.game.nb_players()):
				if self.game.turn_of != i and self.game.isAlive(i):
					ret_str = self.game.damage(self.game.turn_of,i,2,2,self.quotes_on)
					current_message = await self.main_channel.send(ret_str)
					await self.add_message_to_buffer(current_message)

			await self.pillage_victory_and_deaths(self.area_effect_post)

		if card == light.chocolate_bar_card:
			self.game.last_drawn = 1
			self.game.discard_light(card)
			current_message = await self.main_channel.send('Si '+self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' a **un personnage à moins de 11 PV** et est révélé ou se révèle maintenant, toutes ses Blessures seront **soignées**.')
			await self.add_message_to_buffer(current_message)

			# If the player is already revealed and has less than 11 HP, it full heals him automatically
			if (self.game.playerlist[self.game.turn_of].getCharacter().getHP() <= 11) and self.game.isRevealed(self.game.turn_of):
				ret_str = self.game.heal(self.game.turn_of,self.game.turn_of,14,0)
				current_message = await self.main_channel.send(ret_str)
				await self.add_message_to_buffer(current_message)
				await self.area_effect_post()
			# If the player is already revealed and has more than 12 HP, nothing happens
			elif (self.game.playerlist[self.game.turn_of].getCharacter().getHP() >= 12) and self.game.isRevealed(self.game.turn_of):
				current_message = await self.main_channel.send('Rien ne se passe.')
				await self.add_message_to_buffer(current_message)
				await self.area_effect_post()
			else:
				self.last_choice_message = await self.main_channel.send('Voici les actions possibles :\n'
				+ '> Taper **'+self.prefix+'reveal** : te révéler si tu peux et veux utiliser ce soin.\n'
				+ '> \u274C : Ne pas l\'utiliser')
				await self.last_choice_message.add_reaction('\u274C')
				self.game.using_chocolate_bar = True

		if card == light.lay_on_hands_card:
			self.game.last_drawn = 1
			self.game.discard_light(card)
			ret_str = ''
			if self.version == 0:
				ret_str = 'Si '+self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' est un **Hunter** :blue_circle: et est révélé ou se révèle maintenant, toutes ses Blessures seront **soignées**.'
			elif self.version != 0:
				ret_str = 'Si '+self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' est un **Hunter** :blue_circle: ou Métamorphe :red_circle:, et est révélé ou se révèle maintenant, toutes ses Blessures seront **soignées**.'
			current_message = await self.main_channel.send(ret_str)
			await self.add_message_to_buffer(current_message)

			# If the player is already revealed and is a Hunter, it full heals him automatically
			if ((self.game.isHunter(self.game.turn_of)) or (self.game.getCharacter(self.game.turn_of) == character_list.metamorph)) and self.game.isRevealed(self.game.turn_of):
				ret_str = self.game.heal(self.game.turn_of,self.game.turn_of,14,0)
				current_message = await self.main_channel.send(ret_str)
				await self.add_message_to_buffer(current_message)
				await self.area_effect_post()
			# If the player is already revealed and is not a Hunter, nothing happens
			elif ((not self.game.isHunter(self.game.turn_of)) or (self.game.getCharacter(self.game.turn_of) == character_list.metamorph))  and self.game.isRevealed(self.game.turn_of):
				current_message = await self.main_channel.send('Rien ne se passe.')
				await self.add_message_to_buffer(current_message)
				await self.area_effect_post()
			else:
				self.last_choice_message = await self.main_channel.send('Voici les actions possibles :\n'
				+ '> Taper **'+self.prefix+'reveal** : te révéler si tu peux et veux utiliser ce soin.\n'
				+ '> \u274C : Ne pas l\'utiliser')
				await self.last_choice_message.add_reaction('\u274C')
				self.game.using_lay_on_hands = True

		if card == light.first_aid_card:
			self.game.last_drawn = 1
			self.game.discard_light(card)
			current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' peut placer le joueur de son choix à **7** Blessures.')
			await self.add_message_to_buffer(current_message)

			# Preparing the players and the message
			player_str = self.game.print_targets(True,0)
			nobody_str = ''
			if self.version != 0:
				nobody_str = '> Personne \u274C\n'
			self.last_choice_message = await self.main_channel.send('Qui souhaites-tu placer à **7** Blessures ?\n'
				+player_str
				+nobody_str)

			# Preparing the reactions
			await self.game.print_target_reactions(self.last_choice_message,True,0)
			if self.version != 0:
				await self.last_choice_message.add_reaction('\u274C')

		if card == light.benediction_card:
			self.game.last_drawn = 1
			self.game.discard_light(card)
			current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' peut **soigner** un autre joueur d\'autants de Blessures que le résultat d\'un dé 6.')
			await self.add_message_to_buffer(current_message)

			# Preparing the players and the message
			player_str = self.game.print_targets(False,0)
			self.last_choice_message = await self.main_channel.send('Qui souhaites-tu soigner avec la Bénédiction ?\n'
				+player_str)

			# Preparing the reactions
			await self.game.print_target_reactions(self.last_choice_message,False,0)

		if card == light.guardian_angel_card:
			self.game.last_drawn = 1
			current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' est désormais insensible aux attaques jusqu\'à son prochain tour.')
			await self.add_message_to_buffer(current_message)
			self.game.getGuardianAngel(self.game.turn_of)
			await self.area_effect_post()

		if card == light.new_turn_card:
			self.game.last_drawn = 1
			self.game.discard_light(card)
			current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' rejouera un tour à la fin de celui-ci.')
			await self.add_message_to_buffer(current_message)
			self.game.playerlist[self.game.turn_of].turns_left = self.game.playerlist[self.game.turn_of].turns_left+1
			await self.area_effect_post()

		if card == light.hookshot_card:
			self.game.last_drawn = 1
			self.game.discard_light(card)
			current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' peut **se déplacer** sur la même zone que le joueur de son choix.')
			await self.add_message_to_buffer(current_message)

			# Preparing the players and the message
			player_str = self.game.print_targets(False,0)
			self.last_choice_message = await self.main_channel.send('Vers qui souhaites-tu te déplacer ?\n'
				+player_str
				+'> Personne \u274C\n')

			# Preparing the reactions
			await self.game.print_target_reactions(self.last_choice_message,False,0)
			await self.last_choice_message.add_reaction('\u274C')

		if card == light.fraud_repression_card:
			self.game.last_drawn = 1
			self.game.discard_light(card)
			if self.game.someoneElseHasItems(self.game.turn_of) or (not self.game.isInventoryEmpty(self.game.turn_of)):
				gear_str = ''
				for i in range(0,self.game.nb_players()):
					if (not self.game.isInventoryEmpty(i)):
						for j in range(0,len(self.game.lightInventory(i))):
							gear_str = gear_str+'> Défausser '+(self.game.lightInventory(i))[j].getArticleNameEmoji()+' de '+self.game.getName(i)+' '+str(self.game.getEmoji(i))+'\n'
						for j in range(0,len(self.game.darknessInventory(i))):
							gear_str = gear_str+'> Défausser '+(self.game.darknessInventory(i))[j].getArticleNameEmoji()+' de '+self.game.getName(i)+' '+str(self.game.getEmoji(i))+'\n'
				gear_str = gear_str + '> Ne rien défausser \u274C'

				self.last_choice_message = await self.main_channel.send('Tu peux **défausser un équipement** de n\'importe quel joueur. Que souhaites-tu défausser ?\n'+gear_str)

				for i in range(0,self.game.nb_players()):
					if (not self.game.isInventoryEmpty(i)):
						for j in range(0,len(self.game.lightInventory(i))):
							await self.last_choice_message.add_reaction((self.game.lightInventory(i))[j].getEmoji())
						for j in range(0,len(self.game.darknessInventory(i))):
							await self.last_choice_message.add_reaction((self.game.darknessInventory(i))[j].getEmoji())
				await self.last_choice_message.add_reaction('\u274C')
			else:
				current_message = await self.main_channel.send('Il n\'y a rien à défausser.')
				await self.add_message_to_buffer(current_message)
				await self.area_effect_post()


		if card == light.spear_card:
			self.game.last_drawn = 0
			self.game.gainItem(self.game.turn_of,items.spear)
			await self.pillage_victory_and_deaths(self.area_effect_post)

		if card == light.robe_card:
			self.game.last_drawn = 0
			self.game.gainItem(self.game.turn_of,items.robe)
			await self.pillage_victory_and_deaths(self.area_effect_post)

		if card == light.compass_card:
			self.game.last_drawn = 0
			self.game.gainItem(self.game.turn_of,items.compass)
			await self.pillage_victory_and_deaths(self.area_effect_post)

		if card == light.ring_card:
			self.game.last_drawn = 0
			self.game.gainItem(self.game.turn_of,items.ring)
			ret_str = self.game.heal(self.game.turn_of,self.game.turn_of,1,5)
			current_message = await self.main_channel.send(ret_str)
			await self.add_message_to_buffer(current_message)
			await self.pillage_victory_and_deaths(self.area_effect_post)

		if card == light.amulet_card:
			self.game.last_drawn = 0
			self.game.gainItem(self.game.turn_of,items.amulet)
			await self.pillage_victory_and_deaths(self.area_effect_post)

		if card == light.cross_card:
			self.game.last_drawn = 0
			self.game.gainItem(self.game.turn_of,items.cross)
			await self.pillage_victory_and_deaths(self.area_effect_post)

		if card == light.pin_card:
			self.game.last_drawn = 0
			self.game.gainItem(self.game.turn_of,items.pin)
			await self.pillage_victory_and_deaths(self.area_effect_post)

	# Drawing a darkness card

	async def draw_darkness(self):
		card = self.game.draw_one_darkness()

		current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' pioche '+card.fullName()+'.\n')
		await self.add_message_to_buffer(current_message)

		if card == darkness.vampire_bat_card:
			self.game.last_drawn = 2
			self.game.discard_darkness(card)
			current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' doit infliger **2** Blessures à un joueur, puis se soigner **1** Blessure.')
			await self.add_message_to_buffer(current_message)

			# Preparing the players and the message
			player_str = self.game.print_targets(True,3)
			self.last_choice_message = await self.main_channel.send('Qui souhaites-tu vampiriser à l\'aide de la Chauve-souris ?\n'
				+player_str)

			# Preparing the reactions
			await self.game.print_target_reactions(self.last_choice_message,True,0)

		if card == darkness.spider_card:
			self.game.last_drawn = 2
			self.game.discard_darkness(card)
			current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' doit infliger **2** Blessures à un joueur, puis subir **2** Blessure.')
			await self.add_message_to_buffer(current_message)

			# Preparing the players and the message
			player_str = self.game.print_targets(True,3)
			self.last_choice_message = await self.main_channel.send('Qui souhaites-tu faire infester par l\'Araignée ?\n'
				+player_str)

			# Preparing the reactions
			await self.game.print_target_reactions(self.last_choice_message,True,0)

		if card == darkness.dynamite_card:
			self.game.last_drawn = 2
			self.game.discard_darkness(card)
			current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' va lancer la Dynamite ; celle-ci va, selon le résultat des dés, soit désigner un secteur et infliger **3** Blessures à tous les joueurs qui s\'y trouvent, soit ne pas exploser.')
			await self.add_message_to_buffer(current_message)

			# Preparing the players and the message
			self.last_choice_message = await self.main_channel.send('Clique sur les dés \U0001F3B2 pour lancer la Dynamite, '+self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+'.')

			# Preparing the reactions
			await self.last_choice_message.add_reaction('\U0001F3B2')

		if card == darkness.voodoo_doll_card:
			self.game.last_drawn = 2
			self.game.discard_darkness(card)
			current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' va choisir un joueur ; cela lancera un dé 6 ; entre 1 et 4, la cible subit **3** Blessures. Sur 5 ou 6, '+self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' subit **3** Blessures.')
			await self.add_message_to_buffer(current_message)

			# Preparing the players and the message
			player_str = self.game.print_targets(True,2)
			self.last_choice_message = await self.main_channel.send('Qui souhaites-tu maudire avec la Poupée Vaudou ?\n'
				+player_str)

			# Preparing the reactions
			await self.game.print_target_reactions(self.last_choice_message,True,0)

		if card == darkness.devilish_ritual_card:
			self.game.last_drawn = 2
			self.game.discard_darkness(card)
			current_message = await self.main_channel.send('Si '+self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' est un **Shadow** :red_circle: et est révélé ou se révèle maintenant, toutes ses Blessures seront **soignées**.')
			await self.add_message_to_buffer(current_message)

			# If the player is already revealed and is a Shadow, it full heals him automatically
			if (self.game.isShadow(self.game.turn_of)) and self.game.isRevealed(self.game.turn_of):
				ret_str = self.game.heal(self.game.turn_of,self.game.turn_of,14,0)
				current_message = await self.main_channel.send(ret_str)
				await self.add_message_to_buffer(current_message)
				await self.area_effect_post()
			# If the player is already revealed and is not a Shadow, nothing happens
			elif (not self.game.isShadow(self.game.turn_of)) and self.game.isRevealed(self.game.turn_of):
				current_message = await self.main_channel.send('Rien ne se passe.')
				await self.add_message_to_buffer(current_message)
				await self.area_effect_post()
			else:
				self.last_choice_message = await self.main_channel.send('Voici les actions possibles :\n'
				+ '> Taper **'+self.prefix+'reveal** : te révéler si tu peux et veux utiliser ce soin.\n'
				+ '> \u274C : Ne pas l\'utiliser')
				await self.last_choice_message.add_reaction('\u274C')
				self.game.using_devilish_ritual = True

		if card == darkness.whip_card:
			self.game.last_drawn = 2
			self.game.discard_darkness(card)
			current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' peut forcer un joueur à **se déplacer** sur sa zone.')
			await self.add_message_to_buffer(current_message)

			# Preparing the players and the message
			player_str = self.game.print_targets(False,0)
			self.last_choice_message = await self.main_channel.send('Qui souhaites-tu déplacer vers toi ?\n'
				+player_str
				+'> Personne \u274C\n')

			# Preparing the reactions
			await self.game.print_target_reactions(self.last_choice_message,False,0)
			await self.last_choice_message.add_reaction('\u274C')

		if card == darkness.succubus_card:
			self.game.last_drawn = 2
			self.game.discard_darkness(card)
			if self.game.someoneElseHasItems(self.game.turn_of):
				gear_str = ''
				for i in range(0,self.game.nb_players()):
					if (not self.game.isInventoryEmpty(i)) and i != self.game.turn_of:
						for j in range(0,len(self.game.lightInventory(i))):
							gear_str = gear_str+'> Voler '+(self.game.lightInventory(i))[j].getArticleNameEmoji()+' à '+self.game.getName(i)+' '+str(self.game.getEmoji(i))+'\n'
						for j in range(0,len(self.game.darknessInventory(i))):
							gear_str = gear_str+'> Voler '+(self.game.darknessInventory(i))[j].getArticleNameEmoji()+' à '+self.game.getName(i)+' '+str(self.game.getEmoji(i))+'\n'

				self.last_choice_message = await self.main_channel.send('Tu dois **voler un équipement** à un autre joueur. Que souhaites-tu prendre ?\n'+gear_str)

				for i in range(0,self.game.nb_players()):
					if (not self.game.isInventoryEmpty(i)) and i != self.game.turn_of:
						for j in range(0,len(self.game.lightInventory(i))):
							await self.last_choice_message.add_reaction((self.game.lightInventory(i))[j].getEmoji())
						for j in range(0,len(self.game.darknessInventory(i))):
							await self.last_choice_message.add_reaction((self.game.darknessInventory(i))[j].getEmoji())
			else:
				current_message = await self.main_channel.send('Il n\'y a rien à voler.')
				await self.add_message_to_buffer(current_message)
				await self.area_effect_post()

		if card == darkness.banana_peel_card:
			self.game.last_drawn = 2
			self.game.discard_darkness(card)
			if(self.game.isInventoryEmpty(self.game.turn_of)):
				ret_str = self.game.damage(self.game.turn_of,self.game.turn_of,1,8,self.quotes_on)
				current_message = await self.main_channel.send(ret_str)
				await self.add_message_to_buffer(current_message)
				await self.pillage_victory_and_deaths(self.area_effect_post)
			else:
				gear_str = ''
				players_str = ''
				for j in range(0,len(self.game.lightInventory(self.game.turn_of))):
					gear_str = gear_str+'> Donner '+(self.game.lightInventory(self.game.turn_of))[j].getArticleNameEmoji()+'\n'
				for j in range(0,len(self.game.darknessInventory(self.game.turn_of))):
					gear_str = gear_str+'> Donner '+(self.game.darknessInventory(self.game.turn_of))[j].getArticleNameEmoji()+'\n'
				
				players_str = self.game.print_targets(False,0)

				self.last_choice_message = await self.main_channel.send('Tu dois **donner un équipement** à un autre joueur. Que souhaites-tu donner ?\n'+gear_str+'A qui ?\n'+players_str)

				for j in range(0,len(self.game.lightInventory(self.game.turn_of))):
					await self.last_choice_message.add_reaction((self.game.lightInventory(self.game.turn_of))[j].getEmoji())
				for j in range(0,len(self.game.darknessInventory(self.game.turn_of))):
					await self.last_choice_message.add_reaction((self.game.darknessInventory(self.game.turn_of))[j].getEmoji())
				await self.game.print_target_reactions(self.last_choice_message,False,0)

		if card == darkness.gunmachine_card:
			self.game.last_drawn = 0
			self.game.gainItem(self.game.turn_of,items.gunmachine)
			await self.pillage_victory_and_deaths(self.area_effect_post)

		if card == darkness.bow_card:
			self.game.last_drawn = 0
			self.game.gainItem(self.game.turn_of,items.bow)
			await self.pillage_victory_and_deaths(self.area_effect_post)

		if card == darkness.katana_card:
			self.game.last_drawn = 0
			self.game.gainItem(self.game.turn_of,items.katana)
			await self.pillage_victory_and_deaths(self.area_effect_post)

		if card == darkness.axe_card:
			self.game.last_drawn = 0
			self.game.gainItem(self.game.turn_of,items.axe)
			await self.pillage_victory_and_deaths(self.area_effect_post)

		if card == darkness.zweihander_card:
			self.game.last_drawn = 0
			self.game.gainItem(self.game.turn_of,items.zweihander)
			await self.pillage_victory_and_deaths(self.area_effect_post)

		if card == darkness.mace_card:
			self.game.last_drawn = 0
			self.game.gainItem(self.game.turn_of,items.mace)
			await self.pillage_victory_and_deaths(self.area_effect_post)

		if card == darkness.aids_card:
			self.game.last_drawn = 0
			self.game.gainItem(self.game.turn_of,items.aids)
			ret_str = self.game.damage(self.game.turn_of,self.game.turn_of,1,9,self.quotes_on)
			if ret_str != '':
				current_message = await self.main_channel.send(ret_str)
				await self.add_message_to_buffer(current_message)
			await self.pillage_victory_and_deaths(self.area_effect_post)

	# Drawing a vision card

	async def draw_vision(self):
		card = self.game.draw_one_vision()
		self.game.discard_vision(card)
		self.game.current_vision = card
		self.game.last_drawn = 0


		pChan = self.game.getChannel(self.game.turn_of)
		await pChan.send('Voici la vision que tu obtiens :\n'+card.initiatorText())

		target_str = self.game.print_targets(False,5)
		self.last_choice_message = await pChan.send('Qui choisis-tu ?\n'+target_str)
		await self.game.print_target_reactions(self.last_choice_message,False,0)

	# Sending a vision card

	async def send_vision(self,j):

		pChan = self.game.getChannel(j)
		await pChan.send('**'+self.game.getName(self.game.turn_of)+'** '+str(self.game.getEmoji(self.game.turn_of))+' t\'envoie la vision suivante :\n'+self.game.current_vision.receiverText())

		current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' envoie une vision à **'+self.game.getName(j)+'** '+str(self.game.getEmoji(j))+'.')
		await self.add_message_to_buffer(current_message)

		action_str = self.game.print_vision_options(j)
		self.last_choice_message = await pChan.send('Que choisis-tu ?\n'+action_str)
		await self.game.react_vision_options(self.last_choice_message,j)


	# Applies the effect of the haunted forest when victim and effect have been decided
	async def banana_peel_post(self):
		if self.game.player_receiving_item != None and self.game.item_to_give != None:
			ret_str = self.game.giveItem(self.game.turn_of,self.game.player_receiving_item,self.game.item_to_give)
			if self.game.item_to_give == items.aids:
				ret_str = ret_str + '\n'+self.game.damage(self.game.turn_of,self.game.player_receiving_item,1,9,self.quotes_on)
			await self.last_choice_message.delete()
			self.last_choice_message = None
			current_message = await self.main_channel.send(ret_str)
			await self.add_message_to_buffer(current_message)
			self.game.player_receiving_item = None
			self.game.item_to_give = None
			if self.game.getCharacter(self.game.turn_of) == character_list.bob and (self.game.bob_draw) and (self.game.last_drawn != 0) and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of) and self.version != 0:
				await self.pillage_victory_and_deaths(self.bob_redrawing)
			else:
				await self.pillage_victory_and_deaths(self.attack_pre)


	############################# How the bots reacts to reactions

	#@client.event
	async def on_reaction_add(self,reaction,user):

		# When someone reacts to the joining message
		if(prelaunch.creator != None) and  reaction.message.content.startswith(prelaunch.creator.mention+' crée une partie de **Shadow Hunters: Ultimate Cards Expansion**.'):
			# Tries to add the user when computing the condition. If already present or emoji already used, sends an error
			nb_players_before = prelaunch.nb_players()
			try:
				prelaunch.add(user,reaction.emoji)
				await reaction.message.channel.send(user.mention+' '+str(reaction.emoji)+' a rejoint la partie.')
				if (nb_players_before == 3) and (prelaunch.nb_players() == 4):
					await reaction.message.channel.send('4 joueurs sont connectés. **'+prelaunch.creator.display_name+' peut commencer la partie en tapant '+self.prefix+'start**, ou attendre plus de joueurs.')
			except exceptions.AlreadyConnected:
				await reaction.message.channel.send(user.mention+', tu es déjà présent dans la partie.')
			except exceptions.EmojiUsed:
				await reaction.message.channel.send(user.mention+', l\'emoji '+str(reaction.emoji)+' est déjà utilisé.')
			except exceptions.EmojiReserved:
				await reaction.message.channel.send(user.mention+', l\'emoji '+str(reaction.emoji)+' est réservé à d\'autres utilisations dans le jeu, tu ne peux pas t\'en servir.')
			except exceptions.GameFull:
				await reaction.message.channel.send(user.mention+', la partie est déjà complète, tu ne peux pas rejoindre.')
			except exceptions.GameRunning:
				current_message = await reaction.message.channel.send(user.mention+', une partie est déjà en cours, tu ne peux pas rejoindre.')
				await self.add_message_to_buffer(current_message)

		# When quitting the game
		elif reaction.message.content.startswith('Êtes-vous sûrs de vouloir arrêter la partie ?')  and (self.user != user) and self.quit_try:
			if reaction.emoji == '\u2611':
				await self.quit_game()
			elif reaction.emoji == '\u274C':
				self.quit_try = False
				current_message = await reaction.message.channel.send('La partie reprend.')
				await self.add_message_to_buffer(current_message)

		# AIDS turn
		elif reaction.message.content.startswith('Tu dois **lancer un dé** ')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == -1):
			# Clicks on the dice
			if reaction.emoji == '\U0001F3B2':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				dice_result = self.game.d6()
				current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' a fait '+str(dice_result)+'.')
				await self.add_message_to_buffer(current_message)

				if dice_result <= 3:
					ret_str = self.game.damage(self.game.turn_of,self.game.turn_of,1,9,self.quotes_on)
					current_message = await reaction.message.channel.send(ret_str)
					await self.add_message_to_buffer(current_message)
					if (self.game.erik_active and self.game.getCharacter(self.game.turn_of) == character_list.erik):
						self.turn_phase = 0
						target_str = self.game.print_targets(True,8)
						self.last_choice_message = await self.main_channel.send('Tu peux choisir une des actions suivantes :\n'
							+'> Te soigner **3** Blessures \U0001F489\n'
							+'> Désigner **jusqu\'à 3 joueurs** de ton secteur et leur soigner **2** Blessures.\n'
							+' Voici les joueurs présents sur ton secteur :\n'
							+target_str
							+'> Valider pour soigner **moins de 3** joueurs \U0001F6D1')
						await self.last_choice_message.add_reaction('\U0001F489')
						await self.game.print_target_reactions(self.last_choice_message,True,3)
						await self.last_choice_message.add_reaction('\U0001F6D1')
					elif (self.game.getSleepTime(self.game.turn_of) > 0):
						current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' dort et passe son tour.\n')
						await self.add_message_to_buffer(current_message)
						await self.pillage_victory_and_deaths(self.turn_post)
					else:
						await self.pillage_victory_and_deaths(self.moving_pre)

				elif dice_result == 6:
					self.game.discardItem(self.game.turn_of,items.aids)
					current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' défausse '+str(items.aids.getArticleNameEmoji())+'.\n')
					await self.add_message_to_buffer(current_message)
					if (self.game.erik_active and self.game.getCharacter(self.game.turn_of) == character_list.erik):
						self.turn_phase = 0
						target_str = self.game.print_targets(True,8)
						self.last_choice_message = await self.main_channel.send('Tu peux choisir une des actions suivantes :\n'
							+'> Te soigner **3** Blessures \U0001F489\n'
							+'> Désigner **jusqu\'à 3 joueurs** de ton secteur et leur soigner **2** Blessures.\n'
							+' Voici les joueurs présents sur ton secteur :\n'
							+target_str
							+'> Valider pour soigner **moins de 3** joueurs \U0001F6D1')
						await self.last_choice_message.add_reaction('\U0001F489')
						await self.game.print_target_reactions(self.last_choice_message,True,3)
						await self.last_choice_message.add_reaction('\U0001F6D1')
					elif (self.game.getSleepTime(self.game.turn_of) > 0):
						current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' dort et passe son tour.\n')
						await self.add_message_to_buffer(current_message)
						await self.pillage_victory_and_deaths(self.turn_post)
					else:
						await self.pillage_victory_and_deaths(self.moving_pre)

				else:
					target_string = self.game.print_targets(False,0)
					self.last_choice_message = await self.main_channel.send('Tu dois **donner l\'Idole** \U0001F5FF à un autre joueur. Qui choisis-tu ?\n'+target_string)
					await self.game.print_target_reactions(self.last_choice_message,False,0)

		# Giving AIDS
		elif reaction.message.content.startswith('Tu dois **donner l\'Idole** ')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == -1):
			# we test if the player voted on a valid emoji
			target_found = False
			j = -1
			for i in range(0,self.game.nb_players()):
				if self.game.getEmoji(i) == reaction.emoji and self.game.isAlive(i) and i != self.game.turn_of:
					target_found = True
					j = i
			if target_found:
				await self.last_choice_message.delete()
				ret_str = self.game.giveItem(self.game.turn_of,j,items.aids) + '\n' + self.game.damage(self.game.turn_of,j,1,9,self.quotes_on)
				current_message = await reaction.message.channel.send(ret_str)
				await self.add_message_to_buffer(current_message)
				if (self.game.erik_active and self.game.getCharacter(self.game.turn_of) == character_list.erik):
					self.turn_phase = 0
					target_str = self.game.print_targets(True,8)
					self.last_choice_message = await self.main_channel.send('Tu peux choisir une des actions suivantes :\n'
						+'> Te soigner **3** Blessures \U0001F489\n'
						+'> Désigner **jusqu\'à 3 joueurs** de ton secteur et leur soigner **2** Blessures.\n'
						+' Voici les joueurs présents sur ton secteur :\n'
						+target_str
						+'> Valider pour soigner **moins de 3** joueurs \U0001F6D1')
					await self.last_choice_message.add_reaction('\U0001F489')
					await self.game.print_target_reactions(self.last_choice_message,True,3)
					await self.last_choice_message.add_reaction('\U0001F6D1')
				elif (self.game.getSleepTime(self.game.turn_of) > 0):
					current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' dort et passe son tour.\n')
					await self.add_message_to_buffer(current_message)
					await self.pillage_victory_and_deaths(self.turn_post)
				else:
					await self.pillage_victory_and_deaths(self.moving_pre)

		# When a player wants to move at the beginning of his turn
		elif reaction.message.content.startswith('**Clique sur un emoji** pour effectuer une action')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 0):
			# Clicks on the dice
			if reaction.emoji == '\U0001F3B2':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				await self.moving_normal_throw()
			elif reaction.emoji == '\U0001F9ED':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				await self.moving_compass()
			elif reaction.emoji == '\U0001F4A3':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				damage_str = self.game.damage(self.game.turn_of,self.game.turn_of,1,17,self.quotes_on)
				current_message = await self.main_channel.send(damage_str)
				await self.add_message_to_buffer(current_message)
				await self.moving_compass()
			# Mummy's Power
			else:
				# we test if the player voted on a valid emoji
				target_found = False
				j = -1
				for i in range(0,self.game.nb_players()):
					if self.game.getEmoji(i) == reaction.emoji and self.game.isAlive(i) and i != self.game.turn_of:
						target_found = True
						j = i
				if target_found:
					await self.last_choice_message.delete()
					ret_str = self.game.damage(self.game.turn_of,j,3,7,self.quotes_on)
					current_message = await reaction.message.channel.send(ret_str)
					await self.add_message_to_buffer(current_message)
					self.game.mummy_fired = False
					await self.pillage_victory_and_deaths(self.moving_pre)


			# TODO : Add "the player is Emi" in the following choices
			if reaction.emoji == '\U0001F7E9' or reaction.emoji == '\U0001F7EA' or reaction.emoji == '\u2B1C' or reaction.emoji == '\u2B1B' or reaction.emoji == '\U0001F7EB' or reaction.emoji == '\U0001F7E7':
				ret_str = ''
				if reaction.emoji == '\U0001F7E9':
					ret_str = self.game.move_player_directly(self.game.turn_of,location.hermit_lair)
				if reaction.emoji == '\U0001F7EA':
					ret_str = self.game.move_player_directly(self.game.turn_of,location.otherworld_door)
				if reaction.emoji == '\u2B1C':
					ret_str = self.game.move_player_directly(self.game.turn_of,location.monastery)
				if reaction.emoji == '\u2B1B':
					ret_str = self.game.move_player_directly(self.game.turn_of,location.graveyard)
				if reaction.emoji == '\U0001F7EB':
					ret_str = self.game.move_player_directly(self.game.turn_of,location.haunted_forest)
				if reaction.emoji == '\U0001F7E7':
					ret_str = self.game.move_player_directly(self.game.turn_of,location.ancient_sanctuary)
				await self.last_choice_message.delete()
				self.last_choice_message = None
				await self.moving_finish(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' se déplace vers **'+ret_str+'**.')

		# When a player is moving and rolled a 7
		elif reaction.message.content.startswith('Tu as fait 7')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == -2):
			location_id = -1
			# Looks for the location if in the game
			for i in range(0,6):
				if self.game.gamemap[i].getColor() == reaction.emoji and self.game.gamemap[i] != self.game.getLocation(self.game.turn_of):
					location_id = i

			# Moves the player
			if location_id != -1:
				await self.last_choice_message.delete()
				self.last_choice_message = None
				new_loc_str = self.game.move_player_directly(self.game.turn_of,self.game.gamemap[location_id])
				await self.moving_finish(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' se déplace vers **'+new_loc_str+'**.')

		# When a player is moving and uses the compass
		elif reaction.message.content.startswith('Où veux-tu aller ? Voici les choix possibles ')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == -2):
			if reaction.emoji == '\U0001F7E9' or reaction.emoji == '\U0001F7EA' or reaction.emoji == '\u2B1C' or reaction.emoji == '\u2B1B' or reaction.emoji == '\U0001F7EB' or reaction.emoji == '\U0001F7E7':
				ret_str = ''
				if reaction.emoji == '\U0001F7E9':
					ret_str = self.game.move_player_directly(self.game.turn_of,location.hermit_lair)
				if reaction.emoji == '\U0001F7EA':
					ret_str = self.game.move_player_directly(self.game.turn_of,location.otherworld_door)
				if reaction.emoji == '\u2B1C':
					ret_str = self.game.move_player_directly(self.game.turn_of,location.monastery)
				if reaction.emoji == '\u2B1B':
					ret_str = self.game.move_player_directly(self.game.turn_of,location.graveyard)
				if reaction.emoji == '\U0001F7EB':
					ret_str = self.game.move_player_directly(self.game.turn_of,location.haunted_forest)
				if reaction.emoji == '\U0001F7E7':
					ret_str = self.game.move_player_directly(self.game.turn_of,location.ancient_sanctuary)
				await self.last_choice_message.delete()
				self.last_choice_message = None
				await self.moving_finish(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' se déplace vers **'+ret_str+'**.')


		# When a player can draw a card
		elif reaction.message.content.startswith('Tu peux **piocher une carte**')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 1):

			# Clicks on the vision pile
			if reaction.emoji == '\U0001F7E9':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' choisit de **piocher une carte Vision**.')
				await self.add_message_to_buffer(current_message)
				await self.draw_vision()


			# Clicks on the light pile
			if reaction.emoji == '\u2B1C':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' choisit de **piocher une carte Lumière**.')
				await self.add_message_to_buffer(current_message)
				if self.game.getCharacter(self.game.turn_of) == character_list.bob:
					self.game.bob_draw = True
				await self.draw_light()


			# Clicks on the darkness pile
			if reaction.emoji == '\u2B1B':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' choisit de **piocher une carte Ténèbres**.')
				await self.add_message_to_buffer(current_message)
				if self.game.getCharacter(self.game.turn_of) == character_list.bob:
					self.game.bob_draw = True
				await self.draw_darkness()


			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' choisit de **ne pas piocher** de carte.')
				await self.add_message_to_buffer(current_message)
				await self.attack_pre()


		# When a player is sending a vision
		elif reaction.message.content.startswith('Qui choisis-tu ?')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 1):
			# we test if the player voted on a valid emoji
			target_found = False
			j = -1
			for i in range(0,self.game.nb_players()):
				if self.game.getEmoji(i) == reaction.emoji and self.game.isAlive(i) and i != self.game.turn_of:
					target_found = True
					j = i
			if target_found:
				await self.last_choice_message.delete()
				self.last_choice_message = None
				self.game.vision_receiver = j
				await self.send_vision(j)

		# When a player is answering a vision
		elif reaction.message.content.startswith('Que choisis-tu ?')  and (self.turn_phase == 1) and self.game.getUser(self.game.vision_receiver) == user:

			j = self.game.vision_receiver


			# Clicks on the arrow
			if reaction.emoji == '\u27A1':
				await self.last_choice_message.delete()
				self.last_choice_message = None

				pChan = self.game.getChannel(j)
				await pChan.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' connaît maintenant ton personnage.')
				await (self.game.getChannel(self.game.turn_of)).send('Voici son identité :\n'+self.game.getCharacter(j).info())
				current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' **connaît** maintenant **le personnage** de '+self.game.getName(j)+' '+str(self.game.getEmoji(j))+'.')
				await self.add_message_to_buffer(current_message)

				self.game.vision_receiver = None
				await self.pillage_victory_and_deaths(self.area_effect_post)

			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.last_choice_message = None

				pChan = self.game.getChannel(j)
				await pChan.send('Rien ne se passe.')
				await (self.game.getChannel(self.game.turn_of)).send('Rien ne se passe.')
				current_message = await self.main_channel.send('Rien ne se passe.')
				await self.add_message_to_buffer(current_message)

				self.game.vision_receiver = None
				await self.pillage_victory_and_deaths(self.area_effect_post)

			# Clicks on the knife
			elif reaction.emoji == '\U0001FA78':
				await self.last_choice_message.delete()
				self.last_choice_message = None

				pChan = self.game.getChannel(j)
				await pChan.send('Tu as choisi de subir **1** Blessure.')
				await (self.game.getChannel(self.game.turn_of)).send(self.game.getName(j)+' '+str(self.game.getEmoji(j))+' va subir **1** Blessure.')
				ret_str = self.game.damage(self.game.turn_of,j,1,10,self.quotes_on)
				current_message = await self.main_channel.send(ret_str)
				await self.add_message_to_buffer(current_message)

				self.game.vision_receiver = None
				await self.pillage_victory_and_deaths(self.area_effect_post)

			# Clicks on the bomb
			elif reaction.emoji == '\U0001F4A3':
				await self.last_choice_message.delete()
				self.last_choice_message = None

				pChan = self.game.getChannel(j)
				await pChan.send('Tu as choisi de subir **2** Blessures.')
				await (self.game.getChannel(self.game.turn_of)).send(self.game.getName(j)+' '+str(self.game.getEmoji(j))+' va subir **2** Blessures.')
				ret_str = self.game.damage(self.game.turn_of,j,2,10,self.quotes_on)
				current_message = await self.main_channel.send(ret_str)
				await self.add_message_to_buffer(current_message)

				self.game.vision_receiver = None
				await self.pillage_victory_and_deaths(self.area_effect_post)

			# Clicks on the healing
			elif reaction.emoji == '\U0001F489':
				await self.last_choice_message.delete()
				self.last_choice_message = None

				pChan = self.game.getChannel(j)
				await pChan.send('Tu as choisi de te soigner **1** Blessure.')
				await (self.game.getChannel(self.game.turn_of)).send(self.game.getName(j)+' '+str(self.game.getEmoji(j))+' va se soigner **1** Blessure.')
				ret_str = self.game.heal(self.game.turn_of,j,1,6)
				current_message = await self.main_channel.send(ret_str)
				await self.add_message_to_buffer(current_message)

				self.game.vision_receiver = None
				await self.pillage_victory_and_deaths(self.area_effect_post)

			# Else it has to be an item, and we need to know which one
			else:
				# Gets the item to give if it exists
				if items.emoji_to_item_dictionary.get(reaction.emoji,None) != None:

					await self.last_choice_message.delete()
					self.last_choice_message = None

					self.game.item_to_give = items.emoji_to_item_dictionary.get(reaction.emoji,None)

					ret_str = self.game.giveItem(j,self.game.turn_of,self.game.item_to_give)
					# Erreur ici quand on donne le SIDA, apparemment. Rien ne se passe.
					if self.game.item_to_give == items.aids:
						ret_str = ret_str + '\n'+self.game.damage(j,self.game.turn_of,1,9,self.quotes_on)

					pChan = self.game.getChannel(j)
					await pChan.send('Tu as choisi de donner '+self.game.item_to_give.getArticleNameEmoji()+'.')
					await (self.game.getChannel(self.game.turn_of)).send(self.game.getName(j)+' '+str(self.game.getEmoji(j))+' te donne '+self.game.item_to_give.getArticleNameEmoji()+'.')


					current_message = await self.main_channel.send(ret_str)
					await self.add_message_to_buffer(current_message)
					self.game.item_to_give = None

					self.game.vision_receiver = None
					await self.pillage_victory_and_deaths(self.area_effect_post)

		# When a player is on the Haunted Forest
		elif reaction.message.content.startswith('Choisis **une action** et **un joueur**')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 1):

			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' choisit de **ne pas utiliser** le pouvoir des esprits de la Forêt Hantée.')
				await self.add_message_to_buffer(current_message)
				await self.attack_pre()

			# Clicks on the healing
			if reaction.emoji == '\U0001F489':
				self.game.haunted_forest_effect = 1

			# Clicks on the damage
			if reaction.emoji == '\U0001FA78':
				self.game.haunted_forest_effect = -1

			# Else we test if the player voted on a valid emoji
			target_found = False
			j = -1
			for i in range(0,self.game.nb_players()):
				if self.game.getEmoji(i) == reaction.emoji and self.game.isAlive(i):
					target_found = True
					j = i
			if target_found:
				self.game.haunted_forest_victim = j
			await self.haunted_forest_post()
			
		# When a player is on the Ancient Sanctuary
		elif reaction.message.content.startswith('Tu peux **voler un équipement** à un autre joueur. Que souhaites-tu prendre ?')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 1):

			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' choisit de **ne rien voler**.')
				await self.add_message_to_buffer(current_message)
				await self.attack_pre()
			else:
				# We test the player voted on a valid emoji
				await self.last_choice_message.delete()
				target_found = False
				emoji_item = None
				target_player = None
				for i in range(0,self.game.nb_players()):
					if (not self.game.isInventoryEmpty(i)) and i != self.game.turn_of:
						for j in range(0,len(self.game.lightInventory(i))):
							if ((self.game.lightInventory(i))[j].getEmoji() == reaction.emoji):
								target_found = True
								emoji_item = (self.game.lightInventory(i))[j].getEmoji()
								target_player = i
						for j in range(0,len(self.game.darknessInventory(i))):
							if ((self.game.darknessInventory(i))[j].getEmoji() == reaction.emoji):
								target_found = True
								emoji_item = (self.game.darknessInventory(i))[j].getEmoji()
								target_player = i
				if target_found:
					item_to_steal = items.emoji_to_item_dictionary.get(emoji_item,None)
					ret_str = self.game.stealItem(self.game.turn_of,target_player,item_to_steal)
					if item_to_steal == items.aids:
						ret_str = ret_str + '\n'+self.game.damage(self.game.turn_of,self.game.turn_of,1,9,self.quotes_on)
					current_message = await self.main_channel.send(ret_str)
					await self.add_message_to_buffer(current_message)
					await self.pillage_victory_and_deaths(self.attack_pre)

		# When a player wants to attack another
		elif reaction.message.content.startswith('**Clique sur un emoji** pour attaquer un joueur')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 2):
			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' choisit de **n\'attaquer personne**.')
				await self.add_message_to_buffer(current_message)
				await self.turn_post()
			else:
				# We test the player voted on a valid emoji
				await self.last_choice_message.delete()
				target_found = False
				j = -1
				for i in range(0,self.game.nb_players()):
					if self.game.playerlist[i].getEmoji() == reaction.emoji and self.game.playerlist[i].isAlive():
						target_found = True
						j = i
				if target_found:
					await self.attack_mid(j)

		# When Mograine is attacking several targets
		elif reaction.message.content.startswith('**Choisis 2 joueurs** à attaquer (le deuxième ne subira que la moitié des dégâts)')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 2):
			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' choisit de **n\'attaquer personne**.')
				await self.add_message_to_buffer(current_message)
				await self.turn_post()
			elif reaction.emoji == '\U0001F6D1' and self.game.mograine_target_1 != None:
				await self.last_choice_message.delete()
				self.last_choice_message = None
				await self.attack_mid(self.game.mograine_target_1)
			elif self.game.mograine_target_1 == None:
				# We test the player voted on a valid emoji
				target_found = False
				j = -1
				for i in range(0,self.game.nb_players()):
					if self.game.playerlist[i].getEmoji() == reaction.emoji and self.game.playerlist[i].isAlive():
						target_found = True
						j = i
				if target_found:
					self.game.mograine_target_1 = j
			elif self.game.mograine_target_2 == None:
				# We test the player voted on a valid emoji
				await self.last_choice_message.delete()
				self.last_choice_message = None
				target_found = False
				j = -1
				for i in range(0,self.game.nb_players()):
					if self.game.playerlist[i].getEmoji() == reaction.emoji and self.game.playerlist[i].isAlive():
						target_found = True
						j = i
				if target_found:
					self.game.mograine_target_2 = j
					
					await self.attack_mid_mograine()

		# When a player has the gunmachine
		elif reaction.message.content.startswith('Tu as la Mitrailleuse')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 2):
			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' choisit de **ne pas attaquer**.')
				await self.add_message_to_buffer(current_message)
				await self.turn_post()
			elif  reaction.emoji == '\U0001F52B':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				await self.attack_mid_gunmachine()

		# When Despair attacks
		elif reaction.message.content.startswith('Si tu attaques, tous les joueurs (excepté toi) subiront des dégâts.')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 2):
			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' choisit de **ne pas attaquer**.')
				await self.add_message_to_buffer(current_message)
				await self.turn_post()
			elif  reaction.emoji == '\u2620':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				await self.attack_mid_despair()

		# When a player wants to attack another
		elif reaction.message.content.startswith('Veux-tu contre-attaquer')  and (user == self.game.getUser(self.game.werewolf_id)) and (self.turn_phase == 2):
			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				self.game.counterattack_available = False
				current_message = await self.main_channel.send(self.game.getName(self.game.werewolf_id)+' '+str(self.game.getEmoji(self.game.werewolf_id))+' choisit de **ne pas contre-attaquer**.')
				await self.add_message_to_buffer(current_message)
				await self.turn_post()
			elif reaction.emoji == '\u2611':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				self.game.counterattack_available = False
				# Computing the dice_value
				dice_value = abs(self.game.d6()-self.game.d4())
				current_message = await self.main_channel.send(self.game.getName(self.game.werewolf_id)+' '+str(self.game.getEmoji(self.game.werewolf_id))+' a fait '+str(dice_value)+'.')
				await self.add_message_to_buffer(current_message)

				# Lothaire can try to block
				if self.game.getCharacter(self.game.turn_of) == character_list.lothaire and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of):
					block_value = abs(self.game.d6()-self.game.d4())	
					current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' a fait '+str(block_value)+'.')
					await self.add_message_to_buffer(current_message)
					if block_value > dice_value+1 and dice_value > 0:
						damage_str = self.game.damage(self.game.werewolf_id,self.game.turn_of,dice_value,16,self.quotes_on)
					else:
						damage_str = self.game.damage(self.game.werewolf_id,self.game.turn_of,dice_value,15,self.quotes_on)

				else:
					damage_str = self.game.damage(self.game.werewolf_id,self.game.turn_of,dice_value,15,self.quotes_on)

				# Sending messages
				current_message = await self.main_channel.send(damage_str)
				await self.add_message_to_buffer(current_message)
				await self.pillage_victory_and_deaths(self.turn_post)


		# Post death pillage
		elif reaction.message.content.startswith('Tu as tué')  and (user == self.game.getUser(self.game.turn_of)):

			# We test the player voted on a valid emoji
			await self.last_choice_message.delete()
			target_found = False
			emoji_item = None
			i = self.game.waiting_for_pillage[0]
			if (not self.game.isInventoryEmpty(i)):
				for j in range(0,len(self.game.lightInventory(i))):
					if ((self.game.lightInventory(i))[j].getEmoji() == reaction.emoji):
						target_found = True
						emoji_item = (self.game.lightInventory(i))[j].getEmoji()
				for j in range(0,len(self.game.darknessInventory(i))):
					if ((self.game.darknessInventory(i))[j].getEmoji() == reaction.emoji):
						target_found = True
						emoji_item = (self.game.darknessInventory(i))[j].getEmoji()
			if target_found:
				item_to_steal = items.emoji_to_item_dictionary.get(emoji_item,None)
				ret_str = self.game.stealItem(self.game.turn_of,i,item_to_steal)
				if item_to_steal == items.aids:
					ret_str = ret_str + '\n'+self.game.damage(self.game.turn_of,self.game.turn_of,1,9,self.quotes_on)
				current_message = await self.main_channel.send(ret_str)
				await self.add_message_to_buffer(current_message)
				self.game.waiting_for_pillage = self.game.waiting_for_pillage[1:len(self.game.waiting_for_pillage)]
				await self.pillage()


		# When a player is ending an action which he had no control over
		elif reaction.message.content.startswith('Clique ici pour continuer')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 1) and (reaction.emoji == '\u27A1'):
			await self.last_choice_message.delete()
			self.last_choice_message = None
			await self.attack_pre()

		# When a player is ending benefitting from a full heal
		elif reaction.message.content.startswith('Voici les actions possibles :\n> Taper **'+self.prefix+'reveal**') and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 1) and (reaction.emoji == '\u274C') and (self.game.using_chocolate_bar or self.game.using_lay_on_hands or self.game.using_devilish_ritual):
			await self.last_choice_message.delete()
			self.last_choice_message = None
			self.game.using_chocolate_bar = False
			self.game.using_lay_on_hands = False
			self.game.using_devilish_ritual = False
			current_message = await self.main_channel.send('Rien ne se passe.')
			await self.add_message_to_buffer(current_message)
			await self.attack_pre()


		# When a player is using the First-aid
		elif reaction.message.content.startswith('Qui souhaites-tu placer à **7** Blessures ?')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 1):

			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' choisit de **ne pas utiliser** la Trousse de soins.')
				await self.add_message_to_buffer(current_message)
				if self.game.getCharacter(self.game.turn_of) == character_list.bob and (self.game.bob_draw) and (self.game.last_drawn != 0) and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of) and self.version != 0:
					await self.bob_redrawing()
				else:
					await self.attack_pre()

			else:
				# Else we test if the player voted on a valid emoji
				target_found = False
				j = -1
				for i in range(0,self.game.nb_players()):
					if self.game.getEmoji(i) == reaction.emoji and self.game.isAlive(i):
						target_found = True
						j = i
				if target_found:
					await self.last_choice_message.delete()
					self.last_choice_message = None
					ret_str = self.game.damage(self.game.turn_of,j,0,3,self.quotes_on)
					current_message = await self.main_channel.send(ret_str)
					await self.add_message_to_buffer(current_message)
					if self.game.getCharacter(self.game.turn_of) == character_list.bob and (self.game.bob_draw) and (self.game.last_drawn != 0) and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of) and self.version != 0:
						await self.bob_redrawing()
					else:
						await self.attack_pre()


		# When a player is using the Benediction
		elif reaction.message.content.startswith('Qui souhaites-tu soigner avec la Bénédiction ?')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 1):

			# we test if the player voted on a valid emoji
			target_found = False
			j = -1
			for i in range(0,self.game.nb_players()):
				if self.game.getEmoji(i) == reaction.emoji and self.game.isAlive(i) and i != self.game.turn_of:
					target_found = True
					j = i
			if target_found:
				await self.last_choice_message.delete()
				self.last_choice_message = None
				dice_value = self.game.d6()
				current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' a fait '+str(dice_value)+'.')
				await self.add_message_to_buffer(current_message)	
				heal_str = self.game.heal(self.game.turn_of,j,dice_value,3)
				current_message = await self.main_channel.send(heal_str)
				await self.add_message_to_buffer(current_message)
				if self.game.getCharacter(self.game.turn_of) == character_list.bob and (self.game.bob_draw) and (self.game.last_drawn != 0) and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of) and self.version != 0:
					await self.bob_redrawing()
				else:
					await self.attack_pre()

		# When a player is using the Hookshot
		elif reaction.message.content.startswith('Vers qui souhaites-tu te déplacer ?')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 1):

			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' choisit de **ne pas se déplacer**.')
				await self.add_message_to_buffer(current_message)
				if self.game.getCharacter(self.game.turn_of) == character_list.bob and (self.game.bob_draw) and (self.game.last_drawn != 0) and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of) and self.version != 0:
					await self.bob_redrawing()
				else:
					await self.attack_pre()

			else:
				# Else we test if the player voted on a valid emoji
				target_found = False
				j = -1
				for i in range(0,self.game.nb_players()):
					if self.game.getEmoji(i) == reaction.emoji and self.game.isAlive(i):
						target_found = True
						j = i
				if target_found:
					await self.last_choice_message.delete()
					self.last_choice_message = None
					self.game.move_player_directly(self.game.turn_of,self.game.getLocation(j))
					current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' rejoint '+self.game.getName(j)+' '+str(self.game.getEmoji(j))+' sur '+self.game.getLocation(j).getNameArticle()+'.')
					await self.add_message_to_buffer(current_message)
					if self.game.getCharacter(self.game.turn_of) == character_list.bob and (self.game.bob_draw) and (self.game.last_drawn != 0) and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of) and self.version != 0:
						await self.bob_redrawing()
					else:
						await self.attack_pre()

		# When a player uses Fraud Repression
		elif reaction.message.content.startswith('Tu peux **défausser un équipement** de n\'importe quel joueur. Que souhaites-tu défausser ?')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 1):

			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' choisit de **ne rien défausser**.')
				await self.add_message_to_buffer(current_message)
				if self.game.getCharacter(self.game.turn_of) == character_list.bob and (self.game.bob_draw) and (self.game.last_drawn != 0) and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of) and self.version != 0:
					await self.bob_redrawing()
				else:
					await self.attack_pre()
			else:
				# We test the player voted on a valid emoji
				await self.last_choice_message.delete()
				target_found = False
				emoji_item = None
				target_player = None
				for i in range(0,self.game.nb_players()):
					if (not self.game.isInventoryEmpty(i)):
						for j in range(0,len(self.game.lightInventory(i))):
							if ((self.game.lightInventory(i))[j].getEmoji() == reaction.emoji):
								target_found = True
								emoji_item = (self.game.lightInventory(i))[j].getEmoji()
								target_player = i
						for j in range(0,len(self.game.darknessInventory(i))):
							if ((self.game.darknessInventory(i))[j].getEmoji() == reaction.emoji):
								target_found = True
								emoji_item = (self.game.darknessInventory(i))[j].getEmoji()
								target_player = i
				if target_found:
					item_to_discard = items.emoji_to_item_dictionary.get(emoji_item,None)
					self.game.discardItem(target_player,item_to_discard)
					current_message = await self.main_channel.send(self.game.getName(target_player)+' '+str(self.game.getEmoji(target_player))+' défausse '+str(item_to_discard.getArticleNameEmoji())+'.\n')
					await self.add_message_to_buffer(current_message)
					if self.game.getCharacter(self.game.turn_of) == character_list.bob and (self.game.bob_draw) and (self.game.last_drawn != 0) and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of) and self.version != 0:
						await self.pillage_victory_and_deaths(self.bob_redrawing)
					else:
						await self.pillage_victory_and_deaths(self.attack_pre)

		# When a player uses the Succubus
		elif reaction.message.content.startswith('Tu dois **voler un équipement** à un autre joueur. Que souhaites-tu prendre ?')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 1):

			# We test the player voted on a valid emoji
			await self.last_choice_message.delete()
			target_found = False
			emoji_item = None
			target_player = None
			for i in range(0,self.game.nb_players()):
				if (not self.game.isInventoryEmpty(i)) and i != self.game.turn_of:
					for j in range(0,len(self.game.lightInventory(i))):
						if ((self.game.lightInventory(i))[j].getEmoji() == reaction.emoji):
							target_found = True
							emoji_item = (self.game.lightInventory(i))[j].getEmoji()
							target_player = i
					for j in range(0,len(self.game.darknessInventory(i))):
						if ((self.game.darknessInventory(i))[j].getEmoji() == reaction.emoji):
							target_found = True
							emoji_item = (self.game.darknessInventory(i))[j].getEmoji()
							target_player = i
			if target_found:
				item_to_steal = items.emoji_to_item_dictionary.get(emoji_item,None)
				ret_str = self.game.stealItem(self.game.turn_of,target_player,item_to_steal)
				if item_to_steal == items.aids:
					ret_str = ret_str + '\n'+self.game.damage(self.game.turn_of,self.game.turn_of,1,9,self.quotes_on)
				current_message = await self.main_channel.send(ret_str)
				await self.add_message_to_buffer(current_message)
				if self.game.getCharacter(self.game.turn_of) == character_list.bob and (self.game.bob_draw) and (self.game.last_drawn != 0) and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of) and self.version != 0:
					await self.pillage_victory_and_deaths(self.bob_redrawing)
				else:
					await self.pillage_victory_and_deaths(self.attack_pre)

		# When a player fell on the banana peel
		elif reaction.message.content.startswith('Tu dois **donner un équipement** à un autre joueur. Que souhaites-tu donner ?')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 1):

			# Gets the item to give if it exists
			if items.emoji_to_item_dictionary.get(reaction.emoji,None) != None:
				self.game.item_to_give = items.emoji_to_item_dictionary.get(reaction.emoji,None)

			# Else we test if the player voted on a valid emoji
			target_found = False
			j = -1
			for i in range(0,self.game.nb_players()):
				if self.game.getEmoji(i) == reaction.emoji and self.game.isAlive(i) and i != self.game.turn_of:
					target_found = True
					j = i
			if target_found:
				self.game.player_receiving_item = j
			await self.banana_peel_post()

		# When a player is using the Vampire bat
		elif reaction.message.content.startswith('Qui souhaites-tu vampiriser à l\'aide de la Chauve-souris ?')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 1):

			# we test if the player voted on a valid emoji
			target_found = False
			j = -1
			for i in range(0,self.game.nb_players()):
				if self.game.getEmoji(i) == reaction.emoji and self.game.isAlive(i):
					target_found = True
					j = i
			if target_found:
				await self.last_choice_message.delete()
				self.last_choice_message = None
				ret_str = self.game.damage(self.game.turn_of,j,2,4,self.quotes_on)
				current_message = await self.main_channel.send(ret_str)
				await self.add_message_to_buffer(current_message)


				# Testing if someone won
				if self.game.didSomeoneWin():
					await self.victory_message()
				else:
					# Healing the player if he is Alive
					if self.game.isAlive(self.game.turn_of):
						ret_str = self.game.heal(self.game.turn_of,self.game.turn_of,1,4)
						current_message = await self.main_channel.send(ret_str)
						await self.add_message_to_buffer(current_message)
					if self.game.getCharacter(self.game.turn_of) == character_list.bob and (self.game.bob_draw) and (self.game.last_drawn != 0) and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of) and self.version != 0:
						await self.pillage_victory_and_deaths(self.bob_redrawing)
					else:
						await self.pillage_victory_and_deaths(self.attack_pre)

		elif reaction.message.content.startswith('Qui souhaites-tu faire infester par l\'Araignée ?')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 1):

			# we test if the player voted on a valid emoji
			target_found = False
			j = -1
			for i in range(0,self.game.nb_players()):
				if self.game.getEmoji(i) == reaction.emoji and self.game.isAlive(i):
					target_found = True
					j = i
			if target_found:
				await self.last_choice_message.delete()
				self.last_choice_message = None
				ret_str = self.game.damage(self.game.turn_of,j,2,5,self.quotes_on)
				current_message = await self.main_channel.send(ret_str)
				await self.add_message_to_buffer(current_message)

				# Damaging the player if he is Alive
				if self.game.isAlive(self.game.turn_of):
					ret_str = self.game.damage(self.game.turn_of,self.game.turn_of,2,5,self.quotes_on)
					current_message = await self.main_channel.send(ret_str)
					await self.add_message_to_buffer(current_message)

				if self.game.getCharacter(self.game.turn_of) == character_list.bob and (self.game.bob_draw) and (self.game.last_drawn != 0) and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of) and self.version != 0:
					await self.pillage_victory_and_deaths(self.bob_redrawing)
				else:
					await self.pillage_victory_and_deaths(self.attack_pre)

		elif reaction.message.content.startswith('Clique sur les dés \U0001F3B2 pour lancer la Dynamite')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 1)  and (reaction.emoji == '\U0001F3B2'):

			await self.last_choice_message.delete()
			self.last_choice_message = None

			dice_result = abs(self.game.d4()+self.game.d6())
			current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' a fait '+str(dice_result)+'.')
			await self.add_message_to_buffer(current_message)

			if dice_result == 7:
				current_message = await self.main_channel.send('La Dynamite n\'explose pas.')
				await self.add_message_to_buffer(current_message)
				await self.area_effect_post()

			else:
				loc1 = self.game.location_of_result(dice_result)
				loc1_id = self.game.getLocationId(loc1)
				loc2_id = self.game.getIdOfTwinLocation(loc1_id)

				no_one_got_hit = True

				for i in range(0,self.game.nb_players()):
					if self.game.isAlive(i) and ( self.game.getLocation(i) == self.game.gamemap[loc1_id] or self.game.getLocation(i) == self.game.gamemap[loc2_id] ):
						no_one_got_hit = False
						ret_str = self.game.damage(self.game.turn_of,i,3,6,self.quotes_on)
						current_message = await self.main_channel.send(ret_str)
						await self.add_message_to_buffer(current_message)

				if no_one_got_hit:
					current_message = await self.main_channel.send('Personne ne se trouve à cet endroit.')
					await self.add_message_to_buffer(current_message)

				await self.pillage_victory_and_deaths(self.area_effect_post)

		elif reaction.message.content.startswith('Qui souhaites-tu maudire avec la Poupée Vaudou ?')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 1):

			# we test if the player voted on a valid emoji
			target_found = False
			j = -1
			for i in range(0,self.game.nb_players()):
				if self.game.getEmoji(i) == reaction.emoji and self.game.isAlive(i):
					target_found = True
					j = i
			if target_found:
				await self.last_choice_message.delete()
				self.last_choice_message = None
				current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' choisit '+self.game.getName(j)+' '+str(self.game.getEmoji(j))+'.')
				await self.add_message_to_buffer(current_message)
				dice_result = self.game.d6()
				current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' a fait '+str(dice_result)+'.')
				await self.add_message_to_buffer(current_message)

				if dice_result <= 4:
					ret_str = self.game.damage(self.game.turn_of,j,3,7,self.quotes_on)
					current_message = await self.main_channel.send(ret_str)
					await self.add_message_to_buffer(current_message)
				else:
					ret_str = self.game.damage(self.game.turn_of,self.game.turn_of,3,7,self.quotes_on)
					current_message = await self.main_channel.send(ret_str)
					await self.add_message_to_buffer(current_message)

				await self.pillage_victory_and_deaths(self.area_effect_post)

		# When a player is using the Whip
		elif reaction.message.content.startswith('Qui souhaites-tu déplacer vers toi ?')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 1):

			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' choisit de **ne déplacer personne**.')
				await self.add_message_to_buffer(current_message)
				if self.game.getCharacter(self.game.turn_of) == character_list.bob and (self.game.bob_draw) and (self.game.last_drawn != 0) and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of) and self.version != 0:
					await self.bob_redrawing()
				else:
					await self.attack_pre()

			else:
				# Else we test if the player voted on a valid emoji
				target_found = False
				j = -1
				for i in range(0,self.game.nb_players()):
					if self.game.getEmoji(i) == reaction.emoji and self.game.isAlive(i):
						target_found = True
						j = i
				if target_found:
					await self.last_choice_message.delete()
					self.last_choice_message = None
					self.game.move_player_directly(j,self.game.getLocation(self.game.turn_of))
					current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' attire '+self.game.getName(j)+' '+str(self.game.getEmoji(j))+' sur '+self.game.getLocation(j).getNameArticle()+'.')
					await self.add_message_to_buffer(current_message)
					if self.game.getCharacter(self.game.turn_of) == character_list.bob and (self.game.bob_draw) and (self.game.last_drawn != 0) and self.game.isRevealed(self.game.turn_of) and self.game.isAbilityAvailable(self.game.turn_of) and self.version != 0:
						await self.bob_redrawing()
					else:
						await self.attack_pre()


		# When Bob can redraw
		elif reaction.message.content.startswith('Veux-tu piocher une autre carte')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 1):

			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.game.bob_draw = False
				self.game.last_drawn = 0
				self.last_choice_message = None
				await self.attack_pre()
			elif reaction.emoji == '\u2611':
				await self.last_choice_message.delete()
				self.game.bob_draw = False
				self.last_choice_message = None
				if self.game.last_drawn == 1:
					await self.draw_light()
					self.game.last_drawn = 0
				elif self.game.last_drawn == 2:
					self.game.last_drawn = 0
					await self.draw_darkness()


		# When Varimathras is trying to get someone asleep
		elif reaction.message.content.startswith('Tu peux endormir un joueur et lui faire passer ses deux prochains tours.')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 3):

			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				await self.turn_post()

			else:
				# Else we test if the player voted on a valid emoji
				target_found = False
				j = -1
				for i in range(0,self.game.nb_players()):
					if self.game.getEmoji(i) == reaction.emoji and self.game.isAlive(i):
						target_found = True
						j = i
				if target_found:
					await self.last_choice_message.delete()
					self.last_choice_message = None
					self.game.setSleepTime(j,2)
					current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' endort **'+self.game.getName(j)+'** '+str(self.game.getEmoji(j))+' pour **2** tours. Si '+self.game.getName(j)+' '+str(self.game.getEmoji(j))+' subit au moins 2 Blessures en une fois, l\'effet prendra fin et '+self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' se soignera 3 Blessures.')
					await self.add_message_to_buffer(current_message)
					self.game.consumeAbility(self.game.turn_of)
					await self.turn_post()

		# When Georges uses his power
		elif reaction.message.content.startswith('Tu peux infliger autant de Blessures que le résultat d\'un dé 4 à un autre joueur.')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 0):

			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				await self.moving_pre()

			else:
				# Else we test if the player voted on a valid emoji
				target_found = False
				j = -1
				for i in range(0,self.game.nb_players()):
					if self.game.getEmoji(i) == reaction.emoji and self.game.isAlive(i):
						target_found = True
						j = i
				if target_found:
					await self.last_choice_message.delete()
					self.last_choice_message = None
					dice_value = self.game.d4()
					damage_str = self.game.damage(self.game.turn_of,j,dice_value,2,self.quotes_on)
					current_message = await self.main_channel.send(damage_str)
					await self.add_message_to_buffer(current_message)
					self.game.consumeAbility(self.game.turn_of)
					await self.pillage_victory_and_deaths(self.moving_pre)

		# When Franklin uses his power
		elif reaction.message.content.startswith('Tu peux infliger autant de Blessures que le résultat d\'un dé 6 à un autre joueur.')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 0):

			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				await self.moving_pre()

			else:
				# Else we test if the player voted on a valid emoji
				target_found = False
				j = -1
				for i in range(0,self.game.nb_players()):
					if self.game.getEmoji(i) == reaction.emoji and self.game.isAlive(i):
						target_found = True
						j = i
				if target_found:
					await self.last_choice_message.delete()
					self.last_choice_message = None
					dice_value = self.game.d6()
					damage_str = self.game.damage(self.game.turn_of,j,dice_value,2,self.quotes_on)
					current_message = await self.main_channel.send(damage_str)
					await self.add_message_to_buffer(current_message)
					self.game.consumeAbility(self.game.turn_of)
					await self.pillage_victory_and_deaths(self.moving_pre)

		# When Fu-Ka uses her power
		elif reaction.message.content.startswith('Tu peux placer un joueur à 7 Blessures.')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 0):

			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				await self.moving_pre()

			else:
				# Else we test if the player voted on a valid emoji
				target_found = False
				j = -1
				for i in range(0,self.game.nb_players()):
					if self.game.getEmoji(i) == reaction.emoji and self.game.isAlive(i):
						target_found = True
						j = i
				if target_found:
					await self.last_choice_message.delete()
					self.last_choice_message = None
					damage_str = self.game.damage(self.game.turn_of,j,0,3,self.quotes_on)
					current_message = await self.main_channel.send(damage_str)
					await self.add_message_to_buffer(current_message)
					self.game.consumeAbility(self.game.turn_of)
					await self.moving_pre()

		# When Ellen uses her power
		elif reaction.message.content.startswith('Tu peux supprimer le pouvoir d\'un autre joueur.')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 0):

			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				await self.moving_pre()

			else:
				# Else we test if the player voted on a valid emoji
				target_found = False
				j = -1
				for i in range(0,self.game.nb_players()):
					if self.game.getEmoji(i) == reaction.emoji and self.game.isAlive(i):
						target_found = True
						j = i
				if target_found:
					await self.last_choice_message.delete()
					self.last_choice_message = None

					if self.game.isShadow(j) and self.game.playerlist[j].getCharacter() != character_list.metamorph and self.version != 0:
						if (not self.game.isRevealed(j)):
							ret_str = self.game.playerlist[j].reveals()
							current_message = await self.main_channel.send(ret_str)
							await self.add_message_to_buffer(current_message)
						heal_str = self.game.heal(self.game.turn_of,self.game.turn_of,3,9)
						current_message = await self.main_channel.send(heal_str)
						await self.add_message_to_buffer(current_message)

					current_message = await self.main_channel.send('**'+self.game.getName(j)+'** '+str(self.game.getEmoji(j))+' perd son pouvoir jusqu\'à la fin de la partie.\n')
					await self.add_message_to_buffer(current_message)
					self.game.consumeAbility(self.game.turn_of)
					self.game.consumeAbility(j)


					
					await self.moving_pre()

		# When Erik uses his power
		elif reaction.message.content.startswith('Tu peux choisir une des actions suivantes')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 0):

			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				await self.moving_pre()

			# Clicks on the syringe:
			elif reaction.emoji == '\U0001F489':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				heal_str = self.game.heal(self.game.turn_of,self.game.turn_of,3,9)
				current_message = await self.main_channel.send(heal_str)
				await self.add_message_to_buffer(current_message)
				self.game.consumeAbility(self.game.turn_of)
				await self.erik_post()

			# Clicks on the stop sign
			elif reaction.emoji == '\U0001F6D1' and (self.game.erik_target_1 != None or self.game.erik_target_2 != None or self.game.erik_target_3 != None):
				await self.last_choice_message.delete()
				self.last_choice_message = None
				heal_str = ''
				if self.game.erik_target_1 != None:
					heal_str = heal_str + self.game.heal(self.game.turn_of,self.game.erik_target_1,2,9)
				if self.game.erik_target_2 != None:
					heal_str = heal_str + self.game.heal(self.game.turn_of,self.game.erik_target_2,2,9)
				if self.game.erik_target_3 != None:
					heal_str = heal_str + self.game.heal(self.game.turn_of,self.game.erik_target_3,2,9)
				current_message = await self.main_channel.send(heal_str)
				await self.add_message_to_buffer(current_message)
				self.game.consumeAbility(self.game.turn_of)
				await self.erik_post()
			else:
				# Else we test if the player voted on a valid emoji
				target_found = False
				j = -1
				for i in range(0,self.game.nb_players()):
					if self.game.getEmoji(i) == reaction.emoji and self.game.isAlive(i):
						target_found = True
						j = i
				if target_found:
					if self.game.erik_target_1 == None:
						self.game.erik_target_1 = j
					elif self.game.erik_target_2 == None:
						self.game.erik_target_2 = j
					elif self.game.erik_target_3 == None:
						self.game.erik_target_3 = j

					if self.game.erik_target_3 != None:
						await self.last_choice_message.delete()
						self.last_choice_message = None
						heal_str = ''
						heal_str = heal_str + self.game.heal(self.game.turn_of,self.game.erik_target_1,2,9)
						heal_str = heal_str + self.game.heal(self.game.turn_of,self.game.erik_target_2,2,9)
						heal_str = heal_str + self.game.heal(self.game.turn_of,self.game.erik_target_3,2,9)
						current_message = await self.main_channel.send(heal_str)
						await self.add_message_to_buffer(current_message)
						self.game.consumeAbility(self.game.turn_of)
						await self.erik_post()

		# When Majora uses his power
		elif reaction.message.content.startswith('Si tu actives ton pouvoir, les joueurs suivants subiront **2** Blessures.')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 0):

			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				await self.moving_pre()

			elif reaction.emoji == '\u2611':

				await self.last_choice_message.delete()
				self.last_choice_message = None

				# Getting locations ID
				id_of_player_loc = self.game.getLocationId(self.game.getLocation(self.game.turn_of))
				id_of_twin_loc = self.game.getIdOfTwinLocation(id_of_player_loc)

				for j in range(0,self.game.nb_players()):
					away_condition = (self.game.getLocation(j) != self.game.gamemap[id_of_player_loc] and self.game.getLocation(j) != self.game.gamemap[id_of_twin_loc])
					if away_condition and self.game.isAlive(j):
						damage_str = self.game.damage(self.game.turn_of,j,2,12,self.quotes_on)
						current_message = await self.main_channel.send(damage_str)
						await self.add_message_to_buffer(current_message)
				self.game.consumeAbility(self.game.turn_of)
				await self.pillage_victory_and_deaths(self.moving_pre)

		# When the Lich uses his power
		elif reaction.message.content.startswith('Si tu actives ton pouvoir, tu vas pouvoir immédiatement jouer')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 3):

			# Clicks on the cross
			if reaction.emoji == '\u274C':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				await self.turn_post()

			elif reaction.emoji == '\u2611':

				await self.last_choice_message.delete()
				self.last_choice_message = None
				self.game.playerlist[self.game.turn_of].turns_left = self.game.playerlist[self.game.turn_of].turns_left+self.game.nb_dead()
				self.game.consumeAbility(self.game.turn_of)
				await self.delete_buffer()
				await self.next_turn()

		# When Daniel chooses his team
		elif reaction.message.content.startswith('Avec qui souhaites-tu jouer ?')  and (user == self.game.getUser(self.game.daniel_id)):

			if reaction.emoji == '\U0001F535':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				self.game.daniel_allegiance = 'Hunter'
				ret_msg = await self.main_channel.send(self.game.getName(self.game.daniel_id)+' '+str(self.game.getEmoji(self.game.daniel_id))+' joue désormais **avec les Hunters** :blue_circle:'+'\n')
				await self.add_message_to_buffer(ret_msg)
	
				# If player is alive, proceed to attack phase
				if self.game.isAlive(self.game.turn_of):
					await self.future_stored()
				# Else end the turn
				else:
					await self.turn_post()

			elif reaction.emoji == '\U0001F534':
				await self.last_choice_message.delete()
				self.last_choice_message = None
				self.game.daniel_allegiance = 'Shadow'
				ret_msg = await self.main_channel.send(self.game.getName(self.game.daniel_id)+' '+str(self.game.getEmoji(self.game.daniel_id))+' joue désormais **avec les Shadows** :red_circle:'+'\n')
				await self.add_message_to_buffer(ret_msg)
	
				# If player is alive, proceed to attack phase
				if self.game.isAlive(self.game.turn_of):
					await self.future_stored()
				# Else end the turn
				else:
					await self.turn_post()

		# When a player is ending his turn
		elif reaction.message.content.startswith('C\'est la fin de ton tour')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 3) and (reaction.emoji == '\u27A1'):
			await self.last_choice_message.delete()
			self.last_choice_message = None
			await self.delete_buffer()
			if (self.game.getSleepTime(self.game.turn_of) > 0):
				self.game.decreaseSleepTime(self.game.turn_of)
				if (self.game.getSleepTime(self.game.turn_of) == 0):
					current_message = await self.main_channel.send(self.game.getName(self.game.turn_of)+' '+str(self.game.getEmoji(self.game.turn_of))+' **se réveille**.\n')
					await self.add_message_to_buffer(current_message)
					await self.next_turn()
				else:
					await self.next_turn()
			else:
				await self.next_turn()


	#@client.event
	async def on_reaction_remove(self,reaction,user):
		print('Someone removes a reaction')
		# When someone reacts to the joining message
		if (prelaunch.creator != None) and reaction.message.content.startswith(prelaunch.creator.mention+' crée une partie de **Shadow Hunters: Ultimate Cards Expansion**.'):
			print('Trying to remove a reaction on creation message.')
			# Tries to delete the user when computing the condition. If not present, nothing happens.
			try:
				prelaunch.delete(user,reaction.emoji)
				print(user.name+' successfully disconnected from the game.')
				await reaction.message.channel.send(user.mention+' '+str(reaction.emoji)+' a quitté la partie.')
			except exceptions.PlayerNotFound:
				print('Exception caught: '+ user.name + ' tried to disconnect, but was not present in the game.')
			except exceptions.GameRunning:
				await reaction.message.channel.send(user.mention+', tu ne peux pas quitter la partie en cours de route. Mais vous pouvez l\'arrêter totalement avec !quit')

		# When a player is on the Haunted Forest
		elif reaction.message.content.startswith('Choisis **une action** et **un joueur**')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 1):

			# Clicks on the healing or on the damage
			if reaction.emoji == '\U0001F489' or '\U0001FA78':
				self.game.haunted_forest_effect = 0

			# Else we test if the player voted on a valid emoji
			target_found = False
			j = -1
			for i in range(0,self.game.nb_players()):
				if self.game.getEmoji(i) == reaction.emoji and self.game.isAlive(i):
					target_found = True
					j = i
			if target_found:
				self.game.haunted_forest_victim = None

		# When Mograine is attacking several targets
		elif reaction.message.content.startswith('**Choisis 2 joueurs** à attaquer (le deuxième ne subira que la moitié des dégâts)')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 2):
			if self.game.mograine_target_2 == None and reaction.emoji != '\U0001F6D1':
				self.game.mograine_target_1 = None


		# When Erik uses his power
		elif reaction.message.content.startswith('Tu peux choisir une des actions suivantes')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 0):

			# Else we test if the player voted on a valid emoji
			target_found = False
			j = -1
			for i in range(0,self.game.nb_players()):
				if self.game.getEmoji(i) == reaction.emoji and self.game.isAlive(i):
					target_found = True
					j = i
			if target_found:
				if self.game.erik_target_1 == j:
					self.game.erik_target_1 = self.game.erik_target_2
					self.game.erik_target_2 = self.game.erik_target_3
					self.game.erik_target_3 = None
				elif self.game.erik_target_2 == j:
					self.game.erik_target_2 = self.game.erik_target_3
					self.game.erik_target_3 = None
				elif self.game.erik_target_3 == j:
					self.game.erik_target_3 = None

		# When a player uses the Banana Peel
		elif reaction.message.content.startswith('Tu dois **donner un équipement** à un autre joueur. Que souhaites-tu donner ?')  and (user == self.game.getUser(self.game.turn_of)) and (self.turn_phase == 1):

			# Clicks on the healing or on the damage
			if items.emoji_to_item_dictionary.get(reaction.emoji,None) != None:
				self.game.item_to_give = None

			# Else we test if the player voted on a valid emoji
			target_found = False
			j = -1
			for i in range(0,self.game.nb_players()):
				if self.game.getEmoji(i) == reaction.emoji and self.game.isAlive(i) and i != self.game.turn_of:
					target_found = True
					j = i
			if target_found:
				self.game.player_receiving_item = None


	############################# Main function : How the bots reacts to messages

#@client.event
	async def on_message(self,message):

		# The bot never reacts to its own messages
		if message.author == self.user:
			return

		# Someone wants to know the rules
		elif message.content == self.prefix+'abilities':
			current_message = await message.channel.send('Pour utiliser son pouvoir, il faut d\'abord se révéler. Il existe trois types de pouvoirs.\n\n'
				+'*Passif* : un pouvoir passif est un effet qui est constamment appliqué sans que vous n\'ayez à faire quoi que ce soit. Il suffit de vous révéler, et il sera constamment actif.\n\n'
				+'*Conditionné* : un pouvoir conditionné est un pouvoir que vous ne pouvez pas activer manuellement, mais qui peut se déclencher dans certaines situations. Lorsque ces situations se présentent, le jeu vous demandera si vous souhaitez activer votre pouvoir ou non.\n\n'
				+'*Activable* : un pouvoir activable est un pouvoir à activer vous-même avec la commande **'+self.prefix+'pow**. Attention, ces pouvoirs doivent souvent être déclenchés à un moment précis. "Au début de votre tour" signifie : au moment de lancer les dés pour se déplacer. "A la fin de votre tour" signifie : au moment de confirmer au jeu que vous allez finir votre tour. S\'il n\'y a pas plus de précisions, il est activable n\'importe quand, même en dehors de votre tour. Notez qu\'en plus, la plupart de ces pouvoirs sont à usage unique.')
			await self.add_message_to_buffer(message)
			await self.add_message_to_buffer(current_message)

		# Someones wants to see the composition
		elif message.content == self.prefix+'board':
			# If no game is created, then error
			if (not prelaunch.launched()):
				await message.channel.send('Pas de partie en cours.')
			else:
				current_message = await message.channel.send(self.game.get_board())
				await self.add_message_to_buffer(message)
				await self.add_message_to_buffer(current_message)

		# Someones wants to know everything about a character but doesn't know the syntax
		elif message.content == self.prefix+'char':
			current_message = await message.channel.send('Syntaxe attendue : **'+self.prefix+'char** nom_de_personnage')
			await self.add_message_to_buffer(message)
			await self.add_message_to_buffer(current_message)

		# Someones wants to obtain information on a character
		elif message.content.startswith(self.prefix+'char') and (message.content != self.prefix+'charlist'):
			if (len(message.content)==len(self.prefix)+4):
				current_message = await message.channel.send('Tapez **'+self.prefix+'char** *nom_de_personnage* pour tout savoir sur un personnage. La liste des personnages est disponible en tapant **'+self.prefix+'charlist**')
				await self.add_message_to_buffer(message)
				await self.add_message_to_buffer(current_message)
			elif  ((len(message.content)>=len(self.prefix)+5) and message.content[len(self.prefix)+4]==' '):
				char_name = message.content[len(self.prefix)+5:len(message.content)]
				res = character_list.char_dictionary.get(char_name,None)
				if res == None:
					current_message = await message.channel.send('Personnage inconnu. Tapez **'+self.prefix+'charlist')
					await self.add_message_to_buffer(message)
					await self.add_message_to_buffer(current_message)
				else:	
					current_message = await message.channel.send(res.info())
					await self.add_message_to_buffer(message)
					await self.add_message_to_buffer(current_message)

		# Someones wants to know all the characters which can be used in the game
		elif message.content == self.prefix+'charlist':
			ret_str = ''
			if self.version == 0:
				ret_str = 'Hunters :blue_circle: : Ellen, Emi, Franklin, Fu-Ka, Georges, Gregor\n'+'Shadows :red_circle: : Métamorphe, Momie, Liche, Loup-Garou, Valkyrie, Vampire\n'+'Neutres :yellow_circle: : Allie, Agnès, Bob, Catherine, Daniel\n'
			elif self.version == 1:
				ret_str = 'Hunters :blue_circle: : Ellen, Emi, Erik, Franklin, Fu-Ka, Gabrielle, Georges, Gregor, Link, Marth\n'+'Shadows :red_circle: : Charles, Ganondorf, Majora, Métamorphe, Mograine, Momie, Liche, Loup-Garou, Valkyrie, Vampire, Varimathras\n'+'Neutres :yellow_circle: : Allie, Agnès/Angus, Bob/Cartouche, Bryan, Catherine, Daniel, Despair, Neo\n'
			current_message = await message.channel.send(ret_str)
			await self.add_message_to_buffer(message)
			await self.add_message_to_buffer(current_message)

		# Someones wants to see the composition
		elif message.content == self.prefix+'compo':
			current_message = await message.channel.send(prelaunch.composition())
			await self.add_message_to_buffer(message)
			await self.add_message_to_buffer(current_message)

		# Someones wants to see all players connected
		elif message.content == self.prefix+'connected':
			# If no game is created, then error
			if (not prelaunch.created()):
				await message.channel.send('Pas de partie en cours.')
			else:
				current_message = await message.channel.send(prelaunch.players_list_str())
				await self.add_message_to_buffer(message)
				await self.add_message_to_buffer(current_message)

		# Someones tries to create a game
		elif message.content == self.prefix+'create':
			# If a game is already created, then error
			if prelaunch.created():
				current_message = await message.channel.send('Une partie est déjà en préparation.')
				await self.add_message_to_buffer(message)
				await self.add_message_to_buffer(current_message)
			else:
				prelaunch.create(message.author)
				self.main_channel = message.channel
				await self.delete_buffer()
				await message.channel.send(message.author.mention+' crée une partie de **Shadow Hunters: Ultimate Cards Expansion**.\n'
				+'**Rejoignez la partie en ajoutant un emoji en réaction à ce message** ; il servira à vous identifier.\n'
				+'Vous pouvez **changer la version du jeu** avec **'+self.prefix+'set version**.\n'
				+'Une fois prêts, **'+message.author.display_name+' doit taper '+self.prefix+'start pour démarrer**.\n\n')

		# Someones wants to enter debug mode
		elif message.content == self.prefix+'debug':
			# If no game is created, then error
			if self.debug:
				self.debug = False
				current_message = await message.channel.send('Debug-mode désactivé')
				await self.add_message_to_buffer(message)
				await self.add_message_to_buffer(current_message)
			else:
				self.debug = True
				current_message = await message.channel.send('Debug-mode activé')
				await self.add_message_to_buffer(message)
				await self.add_message_to_buffer(current_message)

		# Someones wants to know a command
		elif message.content == self.prefix+'help':
			current_message = await message.channel.send('Voici toutes les commandes utiles à connaître. Si vous avez encore des questions, n\'hésitez pas à demander à mon papa, Bronyx.\n'
					+'\n*Lancement et arrêt d\'une partie*\n'
					+'**'+self.prefix+'create** : crée une partie.\n'
					+'**'+self.prefix+'start** : lance la partie si au moins 4 joueurs sont connectés.\n'
					+'**'+self.prefix+'quit** : efface la partie en cours (qu\'elle soit juste créée ou lancée).\n'
					+'\n*Actions en jeu*\n'
					+'**'+self.prefix+'pow** : utilise votre pouvoir, s\'il est *activable* et si vous le faites au bon moment (cf **'+self.prefix+'abilities**).\n'
					+'**'+self.prefix+'reveal** ou **'+self.prefix+'revelo** : révélez votre identité (utilisable n\'importe quand).\n'
					+'\n*Règles* (utilisables partout, avant ou pendant une partie, même en privé avec le bot)\n'
					+'**'+self.prefix+'abilities**: explique les différents types de pouvoir et les occasions de les utiliser.\n'
					+'**'+self.prefix+'rules**: donne une description rapide des règles.\n'
					+'\n*Informations générales* (utilisables partout, avant ou pendant une partie, même en privé avec le bot)\n'
					+'**'+self.prefix+'char** *nom_de_personnage* : vous présente en détails le personnage souhaité.\n'
					+'**'+self.prefix+'charlist** : Affiche la liste de tous les personnages disponibles dans le jeu.\n'
					+'**'+self.prefix+'item** *nom_objet* : donne la description de l\'équipement souhaité.\n'
					+'**'+self.prefix+'locations**: donne les effets du lieu souhaité.\n'
					+'**'+self.prefix+'new**: donne le dernier patch-note.\n'
					+'**'+self.prefix+'version** : donne la version du jeu actuellement utilisée.\n'
					+'\n*Informations sur une partie* (utilisables partout, avant ou pendant une partie, même en privé avec le bot)\n'
					+'**'+self.prefix+'compo** : affiche le nombre de personnages de chaque couleur pour le nombre de joueurs actuellement connectés.\n'
					+'**'+self.prefix+'connected** : affiche tous les joueurs actuellement connectés à la partie.\n'
					+'\n*Configuration du bot*\n'					
					+'**'+self.prefix+'intro** : présente le bot.\n'
					+'**'+self.prefix+'setSHprefix** *caractère* : modifie le préfixe des commandes par le caractère indiqué (! par défaut).\n'
					+'**'+self.prefix+'set quotes** on/off : active/désactive les citations en jeu.\n'
					+'**'+self.prefix+'set version** *nom_version* : change la version du jeu pour celle spécifiée (*vanilla*, *2020*).\n'
					+'**'+self.prefix+'vote** *question* : organise un référendum pour collecter les avis sur la question spécifiée.\n'
					)
			await self.add_message_to_buffer(message)
			await self.add_message_to_buffer(current_message)

		elif message.content == self.prefix+'id':
			await message.channel.send(str(message.author.id))

		elif message.content == self.prefix+'intro':
			current_message = await message.channel.send(
				'Bonjour à tous. Je suis '
				+self.user.mention
				+', et je suis là pour vous servir d\'interface pour jouer à **Shadow Hunters: Ultimate Cards Expansion**. N\'hésitez pas à faire appel à moi.\nTapez **'+self.prefix+'help** pour afficher la liste de toutes les commandes disponibles.\n\nSi vous remarquez des bugs, des comportements anormaux, si vous avez des questions, si vous avez des suggestions d\'amélioration (sur le jeu ou sur mon ergonomie), n\'hésitez pas à en faire part à mon papa, Bronyx, qui se chargera de me mettre à jour.')
			await self.add_message_to_buffer(message)
			await self.add_message_to_buffer(current_message)

		# Someones wants to know everything about an item
		elif message.content.startswith(self.prefix+'item'):
			if (len(message.content)==len(self.prefix)+4):
				current_message = await message.channel.send('Tapez **'+self.prefix+'item** *nom_objet* pour tout savoir sur un équipement.')
				await self.add_message_to_buffer(message)
				await self.add_message_to_buffer(current_message)
			elif  ((len(message.content)>=len(self.prefix)+5) and message.content[len(self.prefix)+4]==' '):
				loc_name = message.content[len(self.prefix)+5:len(message.content)]
				res = items.item_dictionary.get(loc_name,None)
				if res == None:
					current_message = await message.channel.send('Objet inconnu.')
					await self.add_message_to_buffer(message)
					await self.add_message_to_buffer(current_message)
				else:	
					current_message = await message.channel.send(res.getInfo())
					await self.add_message_to_buffer(message)
					await self.add_message_to_buffer(current_message)

		# Someones wants to kill another player in debug mode
		elif message.content.startswith(self.prefix+'kill'):
			# If no game is created, then error
			if self.debug and (len(message.content)==len(self.prefix)+6) and (self.turn_phase == 0 or self.turn_phase == 3):
				await self.last_choice_message.delete()
				self.last_choice_message = None
				id_name = message.content[-1]
				id = int(id_name)
				damage_str = self.game.damage(self.game.turn_of,id,255,19,False)
				current_message = await self.main_channel.send(damage_str)
				await self.add_message_to_buffer(current_message)
				await self.add_message_to_buffer(message)
				if self.turn_phase == 0:
					await self.pillage_victory_and_deaths(self.moving_pre)
				elif self.turn_phase == 3:
					await self.pillage_victory_and_deaths(self.turn_post)
			else:
				await self.add_message_to_buffer(message)
				await message.add_reaction('\U0001F6AB')

		# Someones wants to know everything about a location
		elif message.content == self.prefix+'locations':
			await self.add_message_to_buffer(message)
			current_message = await message.channel.send(location.hermit_lair.getInfo())
			await self.add_message_to_buffer(current_message)
			current_message = await message.channel.send(location.otherworld_door.getInfo())
			await self.add_message_to_buffer(current_message)
			current_message = await message.channel.send(location.monastery.getInfo())
			await self.add_message_to_buffer(current_message)
			current_message = await message.channel.send(location.graveyard.getInfo())
			await self.add_message_to_buffer(current_message)
			current_message = await message.channel.send(location.haunted_forest.getInfo())
			await self.add_message_to_buffer(current_message)
			current_message = await message.channel.send(location.ancient_sanctuary.getInfo())
			await self.add_message_to_buffer(current_message)

		# Someones wants to know everything about a location
		elif message.content == self.prefix+'new':
			await self.add_message_to_buffer(message)
			current_message = await message.channel.send(
					"**Patch note 2.0.0** (nouveaux personnages et nouvelles fonctionnalités)\n\n"
					+"*Personnages*\n"
					+"- Allie a été retravaillée. Elle doit désormais être en vie sans être révélée pour gagner. Elle n'a plus de pouvoir, mais une contrainte qui l'oblige à mentir à toutes les cartes visions qu'elle reçoit.\n"
					+"- Despair a été ajouté. Il s'agit d'un neutre à 13 PV qui doit être le dernier personnage en vie pour gagner. S'il est vivant et révélé, les Hunters et les Shadows ne peuvent pas gagner (la victoire d'un autre neutre met par contre toujours fin à la partie). Son pouvoir lui permet d'attaquer à chaque tour tous les autres joueurs encore vivants.\n"
					+"- Le pouvoir de Varimathras est ajusté, de \"si la cible se réveille sans avoir pris de dégâts, elle subit 4 Blessures\" à \"si quelqu'un parvient à réveiller la cible en lui infligeant des dégâts, Varimathras se soigne de 3 Blessures\".\n\n"
					+"*Fonctionnalités*\n"
					+"- Il est maintenant possible de revenir à une ancienne version du jeu grâce à la commande **!set version**. De plus, la nouvelle commande **!version** permet de savoir quelle version vous utilisez actuellement. 2 versions du jeu sont implémentées pour l'instant : *vanilla* (jeu de base trouvable en boutique + extension officielle, moins Bryan, Charles et David) et *2020* (la version actuelle).\n"
					+"- Une commande **!vote** a été ajoutée, qui permet d'organiser un référendum (en dehors d'une partie) et de permettre aux joueurs de voter. Ceci n'a aucune incidence sur le fonctionnement du bot, il s'agit purement de garder trace des questions qui ont été posées et de compter les votes, en vue de prévoir les prochaines modifications.)\n")
			await self.add_message_to_buffer(current_message)

		# Someones wants to see the order of the players
		elif message.content == self.prefix+'order':
			# If no game is created, then error
			if (not prelaunch.launched()):
				await message.channel.send('Pas de partie en cours.')
			else:
				current_message = await message.channel.send(self.game.players_order_str())
				await self.add_message_to_buffer(message)
				await self.add_message_to_buffer(current_message)

		# Someones wants to see the information of all players
		elif message.content == self.prefix+'players':
			# If no game is created, then error
			if (not prelaunch.launched()):
				await message.channel.send('Pas de partie en cours.')
			else:
				current_message = await message.channel.send(self.game.get_players_state())
				await self.add_message_to_buffer(message)
				await self.add_message_to_buffer(current_message)

		# Someones wants to reveal themselves
		elif message.content == self.prefix+'pow':
			# If no game is created, then error
			if (not prelaunch.launched()):
				await message.channel.send('Pas de partie en cours.')
			else:
				
				pid = self.game.turn_of
				await self.add_message_to_buffer(message)
				if self.game.getUser(pid) != message.author:
				# The lines above are only useful for testing by myself
					pid = self.game.get_player_id(message.author)

				# at this point, pid is the id of the player who typed the message (with priority to the player whose turn it is, if the same user is several players at once)

				if (not self.game.isRevealed(pid)) or (self.game.getSleepTime(pid) != 0) or (not self.game.isAlive(pid)) or (not self.game.isAbilityAvailable(pid)):
					await message.add_reaction('\U0001F6AB')

				# Power of Gregor
				elif self.game.getCharacter(pid) == character_list.gregor:
					if self.turn_phase != 3 or pid != self.game.turn_of:
						await message.add_reaction('\U0001F6AB')
					else:
						await self.last_choice_message.delete()
						self.last_choice_message = None
						self.game.consumeAbility(pid)
						current_message = await message.channel.send(self.game.getName(pid)+' '+str(self.game.getEmoji(pid))+' est **invulnérable** jusqu\'à son prochain tour.')
						self.game.gainGregorShield(pid)
						await self.add_message_to_buffer(current_message)
						await self.turn_post()

				# Power of Varimathras
				elif self.game.getCharacter(pid) == character_list.varimathras:
					if self.turn_phase != 3 or pid != self.game.turn_of:
						await message.add_reaction('\U0001F6AB')
					else:
						await self.last_choice_message.delete()
						self.last_choice_message = None
						target_str = self.game.print_targets(False,0)
						target_str = target_str + '> Annuler \u274C'
						self.last_choice_message = await message.channel.send('Tu peux endormir un joueur et lui faire passer ses deux prochains tours. Qui choisis-tu ?\n'+target_str)
						await self.game.print_target_reactions(self.last_choice_message,False,0)
						await self.last_choice_message.add_reaction('\u274C')

				# Power of Lich
				elif self.game.getCharacter(pid) == character_list.lich:
					if self.turn_phase != 3 or pid != self.game.turn_of:
						await message.add_reaction('\U0001F6AB')
					else:
						await self.last_choice_message.delete()
						self.last_choice_message = None
						self.last_choice_message = await message.channel.send('Si tu actives ton pouvoir, tu vas pouvoir immédiatement jouer **'+str(self.game.nb_dead())+'** tours supplémentaires.\nValider ?\n')
						await self.last_choice_message.add_reaction('\u2611')
						await self.last_choice_message.add_reaction('\u274C')

				# Power of Allie
				elif self.game.getCharacter(pid) == character_list.allie and self.version == 0:
					self.game.consumeAbility(pid)
					heal_str = self.game.heal(pid,pid,14,0)
					current_message = await message.channel.send(heal_str)
					await self.add_message_to_buffer(current_message)
					await self.update()

				# Power of Agnes
				elif self.game.getCharacter(pid) == character_list.agnes:
					if self.turn_phase != 0 or pid != self.game.turn_of:
						await message.add_reaction('\U0001F6AB')
					else:
						self.game.agnes_switched = True
						self.game.consumeAbility(pid)
						current_message = await message.channel.send(self.game.getName(pid)+' '+str(self.game.getEmoji(pid))+' change sa condition de victoire, et **gagnera si '+self.game.getName((pid+1)%self.game.nb_players())+'** '+str(self.game.getEmoji((pid+1)%self.game.nb_players()))+' **gagne**.')
						await self.add_message_to_buffer(current_message)
						await self.update()

				# Power of Angus
				elif self.game.getCharacter(pid) == character_list.angus:
					if self.turn_phase != 0 or pid != self.game.turn_of:
						await message.add_reaction('\U0001F6AB')
					else:
						self.game.angus_switched = True
						self.game.consumeAbility(pid)
						current_message = await message.channel.send(self.game.getName(pid)+' '+str(self.game.getEmoji(pid))+' change sa condition de victoire, et **gagnera si '+self.game.getName((pid-1)%self.game.nb_players())+'** '+str(self.game.getEmoji((pid-1)%self.game.nb_players()))+' **perd**.')
						await self.add_message_to_buffer(current_message)
						await self.update()

				# Power of Georges
				elif self.game.getCharacter(pid) == character_list.georges:
					if self.turn_phase != 0 or pid != self.game.turn_of:
						await message.add_reaction('\U0001F6AB')
					else:
						await self.last_choice_message.delete()
						self.last_choice_message = None
						target_str = self.game.print_targets(False,0)
						target_str = target_str + '> Annuler \u274C'
						self.last_choice_message = await message.channel.send('Tu peux infliger autant de Blessures que le résultat d\'un dé 4 à un autre joueur. Qui choisis-tu ?\n'+target_str)
						await self.game.print_target_reactions(self.last_choice_message,False,0)
						await self.last_choice_message.add_reaction('\u274C')

				# Power of Franklin
				elif self.game.getCharacter(pid) == character_list.franklin:
					if self.turn_phase != 0 or pid != self.game.turn_of:
						await message.add_reaction('\U0001F6AB')
					else:
						await self.last_choice_message.delete()
						self.last_choice_message = None
						target_str = self.game.print_targets(False,0)
						target_str = target_str + '> Annuler \u274C'
						self.last_choice_message = await message.channel.send('Tu peux infliger autant de Blessures que le résultat d\'un dé 6 à un autre joueur. Qui choisis-tu ?\n'+target_str)
						await self.game.print_target_reactions(self.last_choice_message,False,0)
						await self.last_choice_message.add_reaction('\u274C')

				# Power of Fu-Ka
				elif self.game.getCharacter(pid) == character_list.fuka:
					if self.turn_phase != 0 or pid != self.game.turn_of:
						await message.add_reaction('\U0001F6AB')
					else:
						await self.last_choice_message.delete()
						self.last_choice_message = None
						target_str = self.game.print_targets(False,0)
						target_str = target_str + '> Annuler \u274C'
						self.last_choice_message = await message.channel.send('Tu peux placer un joueur à 7 Blessures. Qui choisis-tu ?\n'+target_str)
						await self.game.print_target_reactions(self.last_choice_message,False,0)
						await self.last_choice_message.add_reaction('\u274C')

				# Power of Ellen
				elif self.game.getCharacter(pid) == character_list.ellen:
					if self.turn_phase != 0 or pid != self.game.turn_of:
						await message.add_reaction('\U0001F6AB')
					else:
						await self.last_choice_message.delete()
						self.last_choice_message = None
						target_str = self.game.print_targets(False,0)
						target_str = target_str + '> Annuler \u274C'
						ret_str = ''
						if self.version == 0:
							ret_str = 'Tu peux supprimer le pouvoir d\'un autre joueur. Qui choisis-tu ?\n'
						elif self.version != 0:
							ret_str = 'Tu peux supprimer le pouvoir d\'un autre joueur. De plus, si c\'est un Shadow autre que Métamorphe, il devra se révéler et tu pourras te soigner **3** Blessures. Qui choisis-tu ?\n'
						self.last_choice_message = await message.channel.send(ret_str+target_str)
						await self.game.print_target_reactions(self.last_choice_message,False,0)
						await self.last_choice_message.add_reaction('\u274C')

				# Power of Erik
				elif self.game.getCharacter(pid) == character_list.erik:
					if self.turn_phase != 0 or pid != self.game.turn_of:
						await message.add_reaction('\U0001F6AB')
					else:
						await self.last_choice_message.delete()
						self.last_choice_message = None
						target_str = self.game.print_targets(True,8)
						self.last_choice_message = await message.channel.send('Tu peux choisir une des actions suivantes :\n'
							+'> Te soigner **3** Blessures \U0001F489\n'
							+'> Désigner **jusqu\'à 3 joueurs** de ton secteur et leur soigner **2** Blessures.\n'
							+'> Annuler \u274C\n'
							+' Voici les joueurs présents sur ton secteur :\n'
							+target_str
							+'> Valider pour soigner **moins de 3** joueurs \U0001F6D1')
						await self.last_choice_message.add_reaction('\U0001F489')
						await self.game.print_target_reactions(self.last_choice_message,True,3)
						await self.last_choice_message.add_reaction('\U0001F6D1')
						await self.last_choice_message.add_reaction('\u274C')

				# Power of Majora
				elif self.game.getCharacter(pid) == character_list.majora:
					if self.turn_phase != 0 or pid != self.game.turn_of:
						await message.add_reaction('\U0001F6AB')
					else:
						await self.last_choice_message.delete()
						self.last_choice_message = None
						target_str = self.game.print_targets(False,6)
						self.last_choice_message = await message.channel.send('Si tu actives ton pouvoir, les joueurs suivants subiront **2** Blessures.\n'+target_str+'Valider ?\n')
						await self.last_choice_message.add_reaction('\u2611')
						await self.last_choice_message.add_reaction('\u274C')
				else:
					await message.add_reaction('\U0001F6AB')

		# Someones wants to reveal themselves
		elif (message.content == self.prefix+'reveal') or (message.content == self.prefix+'revelo'):
			# If no game is created, then error
			if (not prelaunch.launched()):
				await message.channel.send('Pas de partie en cours.')
			else:
				try:
					current_message = await message.channel.send(self.game.reveal_player(message.author))
					self.game.updateAura()
					await self.add_message_to_buffer(message)
					await self.add_message_to_buffer(current_message)

					# If the player is currently benefitting from a full heal, and it's him who's revealing himself
					if self.game.getUser(self.game.turn_of) == message.author:
						if self.game.using_chocolate_bar and self.game.playerlist[self.game.turn_of].getCharacter().getHP() <= 11:
							await self.last_choice_message.delete()
							self.last_choice_message = None
							ret_str = self.game.heal(self.game.turn_of,self.game.turn_of,14,0)
							current_message = await message.channel.send(ret_str)
							await self.add_message_to_buffer(current_message)
							self.game.using_chocolate_bar = False
							await self.area_effect_post()

						if self.game.using_lay_on_hands and (self.game.isHunter(self.game.turn_of)  or (self.game.getCharacter(self.game.turn_of) == character_list.metamorph and self.version != 0)):
							await self.last_choice_message.delete()
							self.last_choice_message = None
							ret_str = self.game.heal(self.game.turn_of,self.game.turn_of,14,0)
							current_message = await message.channel.send(ret_str)
							await self.add_message_to_buffer(current_message)
							self.game.using_lay_on_hands = False
							await self.area_effect_post()

						if self.game.using_devilish_ritual and self.game.isShadow(self.game.turn_of):
							await self.last_choice_message.delete()
							self.last_choice_message = None
							ret_str = self.game.heal(self.game.turn_of,self.game.turn_of,14,0)
							current_message = await message.channel.send(ret_str)
							await self.add_message_to_buffer(current_message)
							self.game.using_devilish_ritual = False
							await self.area_effect_post()
						if self.turn_phase == 0:
							await self.last_choice_message.delete()
							self.last_choice_message = None
							await self.moving_pre()

						if self.turn_phase == 2:
							await self.last_choice_message.delete()
							self.last_choice_message = None
							await self.attack_pre()

						if self.turn_phase == 3:
							await self.last_choice_message.delete()
							self.last_choice_message = None
							await self.turn_post()

					await self.update()
				except exceptions.PlayerNotFound:
					await message.add_reaction('\U0001F6AB')
					print('PlayerNotFound')
					await self.add_message_to_buffer(message)
				except exceptions.AlreadyRevealed:
					await message.add_reaction('\U0001F6AB')
					print('AlreadyRevealed')
					await self.add_message_to_buffer(message)


		# Someones wants to reveal themselves
		elif (message.content == self.prefix+'revealall'):
			# If no game is created, then error
			if (not prelaunch.launched()):
				await message.channel.send('Pas de partie en cours.')
			elif self.debug:
				await self.add_message_to_buffer(message)
				self.game.reveal_all()
				await self.update()


		# Someone wants to know the rules
		elif message.content == self.prefix+'rules':
			current_message = await message.channel.send('**Shadow Hunters: Ultimate Cards Expansion** est un jeu qui se joue au tour par tour sur un plateau. Deux camps s\'affrontent : les Hunters :blue_circle: et les Shadows :red_circle: ; le but de chacun de ces deux camps est d\'exterminer l\'autre. Il existe en plus des personnages Neutres :yellow_circle: qui ont chacun leurs propres conditions de victoire.\n\n'
				+'Chaque tour se divise en plusieurs phases : un joueur lance les dés pour se déplacer, applique l\'effet de la zone où il se trouve (**'+self.prefix+'locations**), puis éventuellement attaquer un joueur parmi ceux qui se trouvent sur le même *secteur* (paire de lieux) que lui.\n\n'
				+'Beaucoup d\'actions vont infliger des dégâts aux personnages du jeu. Lorsqu\'un personnage n\'a plus de points de vie, il décède. Au cours de la partie, les joueurs peuvent décider de révéler leurs personnnages (**'+self.prefix+'reveal**), ce qui leur permet d\'activer leur pouvoir (**'+self.prefix+'abilities** et **'+self.prefix+'char** pour plus d\'informations).\n\n'
				+'Dès qu\'un personnage remplit sa condition de victoire, la partie s\'arrête.')
			await self.add_message_to_buffer(message)
			await self.add_message_to_buffer(current_message)

		# Someone tries to start a game
		elif message.content.startswith(self.prefix+'setSHprefix '):
			lp = len(self.prefix)
			lm = len(message.content)
			if lm > lp+12:
				prefix_suggested = message.content[lp+12:lm]
				if (' ' in prefix_suggested) or ('*' in prefix_suggested) or ('~' in prefix_suggested) or ('_' in prefix_suggested):
					await message.add_reaction('\U0001F6AB')
					await self.add_message_to_buffer(message)
				else:
					self.prefix = message.content[lp+12:lm]
					await message.add_reaction('\U0001F197')
					await self.add_message_to_buffer(message)

		elif message.content.startswith(self.prefix+'set quotes on'):
			self.quotes_on = True
			await message.add_reaction('\U0001F197')
			await self.add_message_to_buffer(message)

		elif message.content.startswith(self.prefix+'set quotes off'):
			self.quotes_on = False
			await message.add_reaction('\U0001F197')
			await self.add_message_to_buffer(message)

		elif message.content.startswith(self.prefix+'set version'):
			# If a game is already launched, then error
			if prelaunch.launched():
				current_message = await message.channel.send('Vous ne pouvez pas changer de version en cours de partie.')
				await self.add_message_to_buffer(message)
				await self.add_message_to_buffer(current_message)
			elif message.content == self.prefix+'set version':
				await message.channel.send('Voici les possibilités :\n'
					+'**'+self.prefix+'set version** *vanilla* : jeu de base et l\'unique extension officielle (moins quelques personnages).\n'
					+'**'+self.prefix+'set version** *2020* : version 2.0\n')
			elif message.content == self.prefix+'set version vanilla':
				self.version = 0
				await message.add_reaction('\U0001F197')
				character_list.update_version(0)
				light.update_version(0)
				darkness.update_version(0)
			elif message.content == self.prefix+'set version 2020':
				self.version = 1
				await message.add_reaction('\U0001F197')
				character_list.update_version(1)
				light.update_version(1)
				darkness.update_version(1)
			else:
				await message.add_reaction('\U0001F6AB')

		# Someones wants to skip his turn
		elif message.content.startswith(self.prefix+'skip'):
			# If no game is created, then error
			if self.debug:
				await self.last_choice_message.delete()
				self.last_choice_message = None
				await self.add_message_to_buffer(message)
				await self.turn_post()
			else:
				await self.add_message_to_buffer(message)
				await message.add_reaction('\U0001F6AB')

		# Someone tries to start a game
		elif message.content == self.prefix+'start':
			# If a game is already launched, then error
			if prelaunch.launched():
				current_message = await message.channel.send('Une partie a déjà commencé.')
				await self.add_message_to_buffer(message)
				await self.add_message_to_buffer(current_message)
			# If no game was created, then error
			elif (not prelaunch.created()):
				await message.channel.send('Veuillez d\'abord créer une partie en tapant **'+self.prefix+'create**.')
			# If the channel is not the game channel
			elif message.channel != self.main_channel:
				await message.channel.send('Tu dois lancer la partie dans '+self.main_channel.mention)
			# If someone else than the creator tries to start
			elif (message.author != prelaunch.creator):
				await message.add_reaction('\U0001F6AB')
			# If not enough players
			elif prelaunch.nb_players() < 4:
				await message.channel.send('Il faut au moins 4 joueurs pour lancer une partie.')
			else:
				await self.launch_game()

		# Someones wants to see the game state
		elif message.content == self.prefix+'state':
			# If no game is created, then error
			if (not prelaunch.launched()):
				await message.channel.send('Pas de partie en cours.')
			else:
				await self.main_channel.send('\_\_\_\_\_\_\_\_\_\_')
				self.board_message = await self.main_channel.send(self.game.get_board())
				await self.main_channel.send('\_\_\_\_\_\_\_\_\_\_')
				self.players_message = await self.main_channel.send(self.game.get_players_state())
				await self.main_channel.send('\_\_\_\_\_\_\_\_\_\_')

		# Someone tries to shut down the whole game
		elif message.content == self.prefix+'quit':
			# If no game was created, then error
			if (not prelaunch.created()):
				await message.add_reaction('\U0001F6AB')
			# If the channel is not the game channel
			elif message.channel != self.main_channel:
				await message.channel.send('Tu dois arrêter la partie dans '+self.main_channel.mention)
			# If someone else than the creator tries to quit
			elif (message.author != prelaunch.creator):
				await message.add_reaction('\U0001F6AB')
			else:
				self.quit_try=True
				current_message = quit_message = await message.channel.send('Êtes-vous sûrs de vouloir arrêter la partie ?')
				await self.add_message_to_buffer(message)
				await self.add_message_to_buffer(current_message)
				await quit_message.add_reaction('\u2611')
				await quit_message.add_reaction('\u274C')

		elif message.content.startswith(self.prefix+'version'):
			if self.version == 0:
				current_message = quit_message = await message.channel.send('Version actuelle : vanilla.')
				await self.add_message_to_buffer(message)
				await self.add_message_to_buffer(current_message)
			elif self.version == 1:
				current_message = quit_message = await message.channel.send('Version actuelle : 2020.')
				await self.add_message_to_buffer(message)
				await self.add_message_to_buffer(current_message)

		elif message.content.startswith(self.prefix+'vote'):
			# If a game is already launched, then error
			if prelaunch.launched():
				current_message = await message.channel.send('Vous ne pouvez pas lancer de vote en cours de partie')
				await self.add_message_to_buffer(message)
				await self.add_message_to_buffer(current_message)
			elif len(message.content) == len(self.prefix)+4:
				await message.channel.send('Syntaxe : **'+self.prefix+'vote** *question*')
			else:
				vote_message = await message.channel.send(message.content[len(self.prefix)+5:len(message.content)])
				await vote_message.add_reaction('\u2611')
				await vote_message.add_reaction('\u274C')

		# Someone posts anything else
		else:
			if self.erasing_messages:
				await message.delete()
			elif message.channel == self.main_channel:
				await self.add_message_to_buffer(message)
