import random
import players
import characters
import character_list
import location
import exceptions
import light
import darkness
import vision
import items

class Game:

	# Player parameters
	playerlist=[]
	nb_hunters=0
	nb_shadows=0
	nb_neutrals=0
	char_pool=[]
	gamemap = location.location_list.copy() # contains order of locations with their descriptions ; WARNING: information of each-player location is in Player class
	turn_of=-1
	game_ended = False

	# Winning conditions parameters
	first_blood = False # While false, Catherine and Daniel can win by dying first.
	agnes_switched = False # Used in the victory condition of Agnes
	neo_target = None # Used in the victory condition of Neo
	neo_revenge_activated = None # While false, Neo only needs to protect the player who plays before her.
	neo_id = None # id of the player playing Neo if it exists

	# Cards piles
	light_pile = light.light_pool.copy()
	light_discarded=[]
	darkness_pile = darkness.darkness_pool.copy()
	darkness_discarded=[]
	vision_pile = []
	vision_discarded=[]

	# Other parameters
	just_died=[]
	haunted_forest_victim = None
	haunted_forest_effect = 0 # 0 = None, 1 = heal, -1 = damage
	item_to_give = None
	player_receiving_item = None # player receiving an item from the one who slipped on the banana
	using_chocolate_bar = False
	using_lay_on_hands = False
	using_devilish_ritual = False
	current_vision = None
	vision_receiver = None
	mummy_fired = True
	mograine_target_1 = None
	mograine_target_2 = None
	counterattack_available = False
	werewolf_id = None
	erik_active = False
	erik_target_1 = None
	erik_target_2 = None
	erik_target_3 = None
	bob_draw = False
	last_drawn = 0 # 0 for nothing or for vision ; 1 for light ; 2 for darkness
	future_after_pillage = None
	waiting_for_pillage = []

	## Initialisation of the game
	def __init__(self,l):

		## Creating the players objects
		newplayer = None
		for i in range(0,len(l)):
			newplayer = players.Player(l[i][0],l[i][1])
			self.playerlist = self.playerlist+[newplayer]
		random.shuffle(self.playerlist)

		sudden_death = False
		#if self.nb_players() > 4:
		#	sudden_death_try = random.randint(1,20)
		#	if sudden_death_try == 1:
		#		sudden_death = True


		## Picking and shuffling the characters
		if self.nb_players() == 4:
			self.nb_hunters=2
			self.nb_shadows=2
			self.nb_neutrals=0
		elif self.nb_players() == 5:
			self.nb_hunters=2
			self.nb_shadows=2
			self.nb_neutrals=1
		elif self.nb_players() == 6:
			self.nb_hunters=2
			self.nb_shadows=2
			self.nb_neutrals=2
		elif self.nb_players() == 7:
			self.nb_hunters=2
			self.nb_shadows=2
			self.nb_neutrals=3
		elif self.nb_players() == 8:
			self.nb_hunters=3
			self.nb_shadows=3
			self.nb_neutrals=2
		self.char_pool=self.char_pool+random.sample(character_list.hunter_list,self.nb_hunters)
		self.char_pool=self.char_pool+random.sample(character_list.shadow_list,self.nb_shadows)
		self.char_pool=self.char_pool+random.sample(character_list.neutral_list,self.nb_neutrals)
		random.shuffle(self.char_pool)

		for i in range(0,len(l)):
			if sudden_death:
				self.playerlist[i].setCharacter(character_list.daniel)
			else:
				self.playerlist[i].setCharacter(self.char_pool[i])
			if self.char_pool[i] == character_list.neo:
				self.neo_id = i
			if self.char_pool[i] == character_list.werewolf:
				self.werewolf_id = i
		self.char_pool=[]

		if sudden_death:
			self.vision_pile = vision.vision_pool_sudden_death.copy()
		elif self.nb_players() == 4:
			self.vision_pile = vision.vision_pool_no_neutral.copy()
		else:
			self.vision_pile = vision.vision_pool_default.copy()


		## Shuffling the game map
		random.shuffle(self.gamemap)

		## Shuffling the cards
		random.shuffle(self.light_pile)
		random.shuffle(self.darkness_pile)
		random.shuffle(self.vision_pile)

		## Randomly placing the players
		for i in range(0,len(l)):
			self.playerlist[i].setLocation(random.choice(self.gamemap))

	## Cleans the object
	def clean(self):
		self.playerlist=[]

	## Useful information on the state of the game
	def nb_players(self):
		return len(self.playerlist)

	def nb_dead(self):
		nb = 0
		for i in range(0,self.nb_players()):
			if not self.isAlive(i):
				nb = nb+1
		return nb

	def players_order_str(self):
		res='Les joueurs jouent dans cet ordre :\n'
		for i in range(0,self.nb_players()):
			res=res+'> '+str(i+1)+') '+self.playerlist[i].getName()+' '+str(self.playerlist[i].getEmoji())+'\n'
		return res

	def get_player(self,player):
		for i in range(0,self.nb_players()):
			if self.playerlist[i].getName() == player.display_name:
				return self.playerlist[i]
		raise exceptions.PlayerNotFound

	def get_player_id(self,player):
		for i in range(0,self.nb_players()):
			if self.playerlist[i].getName() == player.display_name:
				return i
		raise exceptions.PlayerNotFound

	def get_players_state(self):
		res=''
		for i in range(0,self.nb_players()):
			res=res+'> **'+str(i+1)+') '+self.playerlist[i].getName()+'** '+str(self.playerlist[i].getEmoji())
			if(i == self.turn_of):
				res=res+' *(en train de jouer)*'
			res=res+'\n'
			if(self.playerlist[i].isRevealed()):
				res=res+'> '+'Personnage : '+self.playerlist[i].getCharNameColor()+'\n'
			if self.playerlist[i].getCharacter() == character_list.neo and self.neo_revenge_activated and self.isAlive(i):
				res = res+'> Cible : '+self.playerlist[self.neo_target].getName()+' '+str(self.playerlist[self.neo_target].getEmoji())+'\n'
			if self.playerlist[i].getCharacter() == character_list.agnes and self.isRevealed(i):
				if self.agnes_switched:
					res = res+'> Victoire : avec '+self.playerlist[(i+1)%self.nb_players()].getName()+' '+str(self.playerlist[(i+1)%self.nb_players()].getEmoji())+'\n'
				else:
					res = res+'> Victoire : avec '+self.playerlist[(i-1)%self.nb_players()].getName()+' '+str(self.playerlist[(i-1)%self.nb_players()].getEmoji())+'\n'
			if (self.isAlive(i)):
				res=res+'> '+'Blessures : '+str(self.playerlist[i].getWounds())+'/'
				if(self.playerlist[i].isRevealed()):
					res=res+str(self.playerlist[i].getCharacter().getHP())+'\n'
				else:
					res=res+'??\n'
			else:
				res = res+'> Mort\n'
			if (self.playerlist[i].light_inventory != []):
				res = res+'> Inventaire (Lumière) : '
				for j in range(0,len(self.playerlist[i].light_inventory)):
					if j > 0:
						res = res + ' , '
					res = res + self.playerlist[i].light_inventory[j].getNameEmoji()
				res = res+'\n'
			if (self.playerlist[i].darkness_inventory != []):
				res = res+'> Inventaire (Ténèbres) : '
				for j in range(0,len(self.playerlist[i].darkness_inventory)):
					if j > 0:
						res = res + ' , '
					res = res + self.playerlist[i].darkness_inventory[j].getNameEmoji()
				res = res+'\n'
			if (self.hasGregorShield(i) or self.hasGuardianAngel(i) or self.hasAura(i) or (self.getSleepTime(i) > 0)):
				res = res+'> Effets : '
				semicolon = ''
				if (self.hasGregorShield(i)):
					res = res+semicolon+'*Bouclier fantôme*'
					semicolon = ' ; '
				if (self.hasGuardianAngel(i)):
					res = res+semicolon+'*Ange gardien*'
					semicolon = ' ; '
				if (self.hasAura(i)):
					res = res+semicolon+'*Aura de Dévotion*'
					semicolon = ' ; '
				if (self.getSleepTime(i) > 0):
					res = res+semicolon+'*Sommeil ('+str(self.getSleepTime(i))+')*'
					semicolon = ' ; '
				res = res+'\n'
			res=res+'\n'
		return res

	def get_board(self):
		res=''
		for i in range(0,len(self.gamemap)):
			res=res+'> '+self.gamemap[i].getNameColor()+' :\n'
			for j in range(0,len(self.playerlist)):
				if self.playerlist[j].getLocation() == self.gamemap[i] and self.playerlist[j].isAlive():
					res=res+'> \t'+self.playerlist[j].getName()+' '+str(self.playerlist[j].getEmoji())
					if self.playerlist[j].isRevealed():
						res=res+' ('+self.playerlist[j].getCharNameColor()+' )'
					res = res+'\n'
			if i%2 == 1:
				res=res+'\n'
		return res

	def getChannel(self,i):
		return self.playerlist[i].getChannel()

	def getUser(self,i):
		return self.playerlist[i].getUser()

	def getMention(self,i):
		return self.playerlist[i].getMention()

	def getName(self,i):
		return self.playerlist[i].getName()

	def getEmoji(self,i):
		return self.playerlist[i].getEmoji()

	def isAlive(self,i):
		return self.playerlist[i].isAlive()

	def isRevealed(self,i):
		return self.playerlist[i].isRevealed()

	def isHunter(self,i):
		return self.playerlist[i].isHunter()

	def isShadow(self,i):
		return self.playerlist[i].isShadow()

	def isNeutral(self,i):
		return self.playerlist[i].isNeutral()

	def getLocation(self,i):
		return self.playerlist[i].getLocation()

	def getCharacter(self,i):
		return self.playerlist[i].getCharacter()

	def location_of_result(self,dice_result):
		if dice_result == 2 or dice_result == 3:
			return location.hermit_lair
		elif dice_result == 4 or dice_result == 5:
			return location.otherworld_door
		elif dice_result == 6:
			return location.monastery
		elif dice_result == 8:
			return location.graveyard
		elif dice_result == 9:
			return location.haunted_forest
		elif dice_result == 10:
			return location.ancient_sanctuary

	def getLocationId(self,location):
		for i in range(0,len(self.gamemap)):
			if self.gamemap[i] == location:
				return i
		return -1

	def getIdOfTwinLocation(self,loc_id):
		if loc_id == 0:
			return 1
		elif loc_id == 1:
			return 0
		elif loc_id == 2:
			return 3
		elif loc_id == 3:
			return 2
		elif loc_id == 4:
			return 5
		elif loc_id == 5:
			return 4

	def getIdOfOtherNearbyLocation(self,loc_id):
		if loc_id == 0:
			return 5
		elif loc_id == 1:
			return 2
		elif loc_id == 2:
			return 1
		elif loc_id == 3:
			return 4
		elif loc_id == 4:
			return 3
		elif loc_id == 5:
			return 0

	def hasGuardianAngel(self,i):
		return self.playerlist[i].hasGuardianAngel()

	def isInventoryEmpty(self,i):
		return self.playerlist[i].isInventoryEmpty()

	def someoneElseHasItems(self,i):
		found = False
		for j in range(0,self.nb_players()):
			if i != j and (not self.isInventoryEmpty(j)):
				found = True
				break
		return found

	def someoneDeadHasItems(self,i):
		found = False
		for j in range(0,len(self.just_died)):
			if i != self.just_died[j] and (not self.isInventoryEmpty(self.just_died[j])):
				found = True
				break
		return found


	def lightInventory(self,i):
		return self.playerlist[i].lightInventory()

	def darknessInventory(self,i):
		return self.playerlist[i].darknessInventory()

	def hasItem(self,i,item):
		return self.playerlist[i].hasItem(item)

	def spearAvailable(self,i):
		return (self.hasItem(i,items.spear) and self.isRevealed(i) and (self.isHunter(i) or self.getCharacter(i) == character_list.metamorph))

	def isAbilityAvailable(self,i):
		return self.playerlist[i].isAbilityAvailable()

	def hasAura(self,i):
		return self.playerlist[i].hasAura()

	def hasGregorShield(self,i):
		return self.playerlist[i].hasGregorShield()

	def getSleepTime(self,i):
		return self.playerlist[i].getSleepTime()

	def nbPlayersReachable(self,i):
		nb = 0
		# Getting locations ID
		id_of_player_loc = self.getLocationId(self.getLocation(i))
		id_of_twin_loc = self.getIdOfTwinLocation(id_of_player_loc)

		for j in range(0,self.nb_players()):
			if self.isAlive(j) and (j != i):

				no_bow_condition = (self.getLocation(j) == self.gamemap[id_of_player_loc] or self.getLocation(j) == self.gamemap[id_of_twin_loc]) and not self.hasItem(i,items.bow)
				away_condition = (self.getLocation(j) != self.gamemap[id_of_player_loc] and self.getLocation(j) != self.gamemap[id_of_twin_loc])
				bow_condition = away_condition and self.hasItem(i,items.bow)

				if( bow_condition or no_bow_condition ):
					nb = nb+1
		return nb

	## Verifying winning conditions
	def didHuntersWin(self):
		exists_hunter = False
		all_shadows_dead = True
		for i in range(0,self.nb_players()):
			if self.playerlist[i].isShadow() and self.playerlist[i].isAlive():
				all_shadows_dead = False
			if self.playerlist[i].isHunter():
				exists_hunter = True
		return (exists_hunter and all_shadows_dead)

	def didShadowsWin(self):
		exists_shadow = False
		all_hunters_dead = True
		for i in range(0,self.nb_players()):
			if self.playerlist[i].isHunter() and self.playerlist[i].isAlive():
				all_hunters_dead = False
			if self.playerlist[i].isShadow():
				exists_shadow = True
		return (exists_shadow and all_hunters_dead)


	def didPlayerWin(self,i):
		if self.playerlist[i].isShadow():
			return self.didShadowsWin()
		elif self.playerlist[i].isHunter():
			return self.didHuntersWin()

		elif self.playerlist[i].getCharacter() == character_list.allie:
			return self.game_ended and self.playerlist[i].isAlive()

		elif self.playerlist[i].getCharacter() == character_list.agnes:
			return self.game_ended and ( 
							(self.agnes_switched and self.didPlayerWin((i+1)%self.nb_players()) ) 
							or ( (not self.agnes_switched) and self.didPlayerWin((i-1)%self.nb_players()) ) 
						   )

		elif self.playerlist[i].getCharacter() == character_list.bob:
			return len(self.lightInventory(i))+len(self.darknessInventory(i)) >= 4

		elif self.playerlist[i].getCharacter() == character_list.bryan:
			return self.playerlist[i].isAlive() and (not self.playerlist[(i+1)%self.nb_players()].isAlive()) and (not self.playerlist[(i-1)%self.nb_players()].isAlive())

		elif self.playerlist[i].getCharacter() == character_list.daniel:
			all_shadows_dead = True
			for j in range(0,self.nb_players()):
				if self.playerlist[j].isShadow() and self.playerlist[j].isAlive():
					all_shadows_dead = False
			return ((not self.first_blood) and (not self.playerlist[i].isAlive())) or (self.first_blood and self.playerlist[i].isAlive() and all_shadows_dead)

		elif self.playerlist[i].getCharacter() == character_list.catherine:
			nb_alive = 0
			for j in range(0,self.nb_players()):
				if self.playerlist[j].isAlive():
					nb_alive = nb_alive+1
			return ((not self.first_blood) and (not self.playerlist[i].isAlive())) or (self.first_blood and self.playerlist[i].isAlive() and nb_alive <= 2)

		elif self.playerlist[i].getCharacter() == character_list.neo:
			return (self.game_ended and (not self.neo_revenge_activated) and self.playerlist[(i-1)%self.nb_players()].isAlive()) or (self.neo_revenge_activated and self.playerlist[i].isAlive() and (not self.playerlist[self.neo_target].isAlive()))
		else:
			return False

	def didSomeoneWin(self):
		for i in range(0,self.nb_players()):
			if self.didPlayerWin(i):
				return True
		return False

	def postDeathEffects(self):
		ret_str = ''
		if (self.just_died != []):
			self.first_blood = True
			self.updateAura()

			# Searching for Daniel
			for i in range(0,self.nb_players()):
				if self.playerlist[i].getCharacter() == character_list.daniel and not self.isRevealed(i):
					ret_str = ret_str+self.playerlist[i].reveals()+'\n'

			# Other effects
			for k in range(0,len(self.just_died)):
				j = self.just_died[k]

				# If the player had a special status, it disappears
				self.loseGuardianAngel(j)
				self.discard_light(light.guardian_angel_card)
				self.loseAura(j)

				# If the player had additional turns, they are lost
				self.playerlist[j].turns_left = 0

				# If the next player after one of the victims is Neo and is alive
				next_id = (j+1)%self.nb_players()
				if self.playerlist[next_id].getCharacter() == character_list.neo and self.isAlive(next_id):
					# If the player killed himself or if Neo killed him, then Neo dies
					if (self.turn_of == j) or (self.turn_of == next_id):
						ret_str = ret_str+self.damage(next_id,next_id,200,-1)+'\n'
					# Else
					else:
						# Reveal if not already done
						if not (self.playerlist[next_id].isRevealed()):
							ret_str = ret_str+self.playerlist[next_id].reveals()+'\n'
						# Activate revenge
						self.neo_target = self.turn_of
						self.neo_revenge_activated = True
						ret_str = ret_str = ret_str+self.playerlist[next_id].getName()+' '+str(self.playerlist[next_id].getEmoji())+' peut **gagner** dès que **'+self.playerlist[self.neo_target].getName()+'** '+str(self.playerlist[self.neo_target].getEmoji())+' **meurt**.'
				# If Bryan is the neighbour of one of the victims
				if self.playerlist[self.turn_of].getCharacter() == character_list.bryan and next_id != self.turn_of and (j-1)%self.nb_players() != self.turn_of :
					ret_str = ret_str+self.playerlist[self.turn_of].reveals()+'\n'

				# Discard items
				self.discardInventory(j)

			self.just_died = []

		return ret_str


	## Small actions
	def d4(self):
		return random.randint(1,4)

	def d6(self):
		return random.randint(1,6)

	def draw_one_light(self):
		if self.light_pile == []:
			self.light_pile = self.light_discarded.copy()
			self.light_discarded = []
			random.shuffle(self.light_pile)
		chosen_card = self.light_pile[0]
		self.light_pile = self.light_pile[1:len(self.light_pile)]
		return chosen_card

	def discard_light(self,card):
		self.light_discarded = self.light_discarded + [card]

	def draw_one_darkness(self):
		if self.darkness_pile == []:
			self.darkness_pile = self.darkness_discarded.copy()
			self.darkness_discarded = []
			random.shuffle(self.darkness_pile)
		chosen_card = self.darkness_pile[0]
		self.darkness_pile = self.darkness_pile[1:len(self.darkness_pile)]
		return chosen_card

	def discard_darkness(self,card):
		self.darkness_discarded = self.darkness_discarded + [card]

	def draw_one_vision(self):
		if self.vision_pile == []:
			self.vision_pile = self.vision_discarded.copy()
			self.vision_discarded = []
			random.shuffle(self.vision_pile)
		chosen_card = self.vision_pile[0]
		self.vision_pile = self.vision_pile[1:len(self.vision_pile)]
		return chosen_card

	def discard_vision(self,card):
		self.vision_discarded = self.vision_discarded + [card]

	def getGuardianAngel(self,i):
		self.playerlist[i].getGuardianAngel()

	def loseGuardianAngel(self,i):
		self.playerlist[i].loseGuardianAngel()

	def gainItem(self,i,item):
		self.playerlist[i].gainItem(item)

	def loseItem(self,i,item):
		self.playerlist[i].loseItem(item)

	def discardItem(self,i,item):
		if item == items.bow:
			self.discard_darkness(darkness.bow_card)
		elif item == items.zweihander:
			self.discard_darkness(darkness.zweihander_card)
		elif item == items.axe:
			self.discard_darkness(darkness.axe_card)
		elif item == items.aids:
			self.discard_darkness(darkness.aids_card)
		elif item == items.katana:
			self.discard_darkness(darkness.katana_card)
		elif item == items.mace:
			self.discard_darkness(darkness.mace_card)
		elif item == items.gunmachine:
			self.discard_darkness(darkness.gunmachine_card)
		elif item == items.amulet:
			self.discard_light(light.amulet_card)
		elif item == items.ring:
			self.discard_light(light.ring_card)
		elif item == items.compass:
			self.discard_light(light.compass_card)
		elif item == items.pin:
			self.discard_light(light.pin_card)
		elif item == items.cross:
			self.discard_light(light.cross_card)
		elif item == items.spear:
			self.discard_light(light.spear_card)
		elif item == items.robe:
			self.discard_light(light.robe_card)
		self.loseItem(i,item)

	def discardInventory(self,i):
		while (self.lightInventory(i) != []):
			item = (self.lightInventory(i))[0]
			self.discardItem(i,item)
		while (self.darknessInventory(i) != []):
			item = (self.darknessInventory(i))[0]
			self.discardItem(i,item)

	def consumeAbility(self,i):
		self.playerlist[i].consumeAbility()

	def gainAura(self,i):
		self.playerlist[i].gainAura()

	def loseAura(self,i):
		self.playerlist[i].loseAura()

	def gainGregorShield(self,i):
		self.playerlist[i].gainGregorShield()

	def loseGregorShield(self,i):
		self.playerlist[i].loseGregorShield()

	def setSleepTime(self,i,k):
		self.playerlist[i].setSleepTime(k)

	def decreaseSleepTime(self,i):
		self.playerlist[i].decreaseSleepTime()

	# Moving players
	def setLocation(self,i,location):
		self.playerlist[i].setLocation(location)

	def move_player_to(self,player_id,dice_result):
		loc = self.location_of_result(dice_result)
		self.setLocation(player_id,loc)
		self.updateAura()
		return loc.getNameArticle()

	def move_player_directly(self,player_id,loc):
		self.setLocation(player_id,loc)
		self.updateAura()
		return loc.getNameArticle()

	## Some modifiers
	def reveal_all(self):
		res=''
		for i in range(0,self.nb_players()):
			if (not self.playerlist[i].isRevealed()):
				res=res+self.playerlist[i].reveals()+'\n'

	def reveal_player(self,player):
		if self.getUser(self.turn_of) == player:
			return self.playerlist[self.turn_of].reveals()
		else:
			# Only this line is useful ; the rest is useful for tests when I play different roels.
			return self.get_player(player).reveals()

	# Steal item
	def stealItem(self,i,j,item):
		# TODO : particular case of AIDS
		self.loseItem(j,item)
		self.gainItem(i,item)
		ret_str = ''
		if item == items.ring:
			ret_str = '\n'+self.heal(i,i,1,5)
		return self.getName(i)+' '+str(self.getEmoji(i))+' vole '+item.getArticleNameEmoji()+' à **'+self.getName(j)+'** '+str(self.getEmoji(j))+ret_str

	# Steal item
	def giveItem(self,i,j,item):
		# TODO : particular case of AIDS
		self.loseItem(i,item)
		self.gainItem(j,item)
		ret_str = ''
		if item == items.ring:
			ret_str = '\n'+self.heal(j,j,1,5)
		return self.getName(i)+' '+str(self.getEmoji(i))+' donne '+item.getArticleNameEmoji()+' à **'+self.getName(j)+'** '+str(self.getEmoji(j))+ret_str

	# Steal Inventory
	def stealInventory(self,i,j):
		ret_str = ''
		while(self.lightInventory(j) != []):
			ret_str = ret_str + self.stealItem(i,j,(self.lightInventory(j))[0]) +'\n'
		while(self.darknessInventory(j) != []):
			ret_str = ret_str + self.stealItem(i,j,(self.darknessInventory(j))[0]) +'\n'
		return ret_str

	# Updates the aura for each player
	def updateAura(self):
		gabrielle_id = -1
		for j in range(0,self.nb_players()):
			if self.getCharacter(j) == character_list.gabrielle and self.isAlive(j) and self.isAbilityAvailable(j) and self.isRevealed(j):
				gabrielle_id = j

		if gabrielle_id == -1:
			for j in range(0,self.nb_players()):
				self.loseAura(j)
		else:
			id_of_player_loc = self.getLocationId(self.getLocation(gabrielle_id))
			id_of_twin_loc = self.getIdOfTwinLocation(id_of_player_loc)	
			for j in range(0,self.nb_players()):
				same_sector_condition = (self.getLocation(j) == self.gamemap[id_of_player_loc] or self.getLocation(j) == self.gamemap[id_of_twin_loc])
				if self.isHunter(j) and self.isAlive(j) and self.isRevealed(j) and same_sector_condition:
					self.gainAura(j)
				else:
					self.loseAura(j)

	# Prints all options of player j when receiving the card stored in self.current_vision
	def print_vision_options(self,j):
		gear_str = ''
		gear_str_lie = ''
		for k in range(0,len(self.lightInventory(j))):
			gear_str = gear_str + '> Donner '+((self.lightInventory(j))[k]).getArticleNameEmoji()
			gear_str_lie = gear_str_lie + '> Donner '+((self.lightInventory(j))[k]).getArticleNameEmoji()+' (Mentir)'
			gear_str = gear_str +'\n'
			gear_str_lie = gear_str_lie +'\n'
		for k in range(0,len(self.darknessInventory(j))):
			gear_str = gear_str + '> Donner '+((self.darknessInventory(j))[k]).getArticleNameEmoji()
			gear_str_lie = gear_str_lie + '> Donner '+((self.darknessInventory(j))[k]).getArticleNameEmoji()+' (Mentir)'
			gear_str = gear_str +'\n'
			gear_str_lie = gear_str_lie +'\n'

		if self.current_vision == vision.mortifere:
			ret_str = ''
			if self.getCharacter(j) == character_list.metamorph:
				ret_str = ret_str+'> Rien ne se passe \u274C\n'
				if self.hasItem(j,items.robe):
					ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78 (Mentir)\n'
				else:
					ret_str = ret_str+'> Subir **1** Blessure \U0001FA78 (Mentir)\n'
			elif not self.isHunter(j):
				ret_str = ret_str+'> Rien ne se passe \u274C\n'
			elif self.hasGregorShield(j):
				ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
			elif self.hasItem(j,items.robe):
				ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
			else:
				ret_str = ret_str+'> Subir **1** Blessure \U0001FA78\n'
			return ret_str
		elif self.current_vision == vision.foudroyante:
			ret_str = ''
			if self.getCharacter(j) == character_list.metamorph:
				if self.hasItem(j,items.robe):
					ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
				else:
					ret_str = ret_str+'> Subir **1** Blessure \U0001FA78\n'
				ret_str = ret_str+'> Rien ne se passe \u274C (Mentir)\n'
			elif not self.isShadow(j):
				ret_str = ret_str+'> Rien ne se passe \u274C\n'
			elif self.hasGregorShield(j):
				ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
			elif self.hasItem(j,items.robe):
				ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
			else:
				ret_str = ret_str+'> Subir **1** Blessure \U0001FA78\n'
			return ret_str
		elif self.current_vision == vision.purificatrice:
			ret_str = ''
			if self.getCharacter(j) == character_list.metamorph:
				if self.hasItem(j,items.robe):
					ret_str = ret_str+'> Subir **1** Blessure (Absorbé : 1) \U0001F4A3\n'
				else:
					ret_str = ret_str+'> Subir **2** Blessures \U0001F4A3\n'
				ret_str = ret_str+'> Rien ne se passe \u274C (Mentir)\n'
			elif not self.isShadow(j):
				ret_str = ret_str+'> Rien ne se passe \u274C\n'
			elif self.hasGregorShield(j):
				ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 2) \U0001F4A3\n'
			elif self.hasItem(j,items.robe):
				ret_str = ret_str+'> Subir **1** Blessure (Absorbé : 1) \U0001F4A3\n'
			else:
				ret_str = ret_str+'> Subir **2** Blessures \U0001F4A3\n'
			return ret_str
		elif self.current_vision == vision.divine:
			ret_str = ''
			if self.getCharacter(j) == character_list.metamorph:
				ret_str = ret_str+'> Rien ne se passe \u274C\n'
				if self.playerlist[j].wounds > 0:
					ret_str = ret_str+'> Soigner **1** Blessure \U0001F489 (Mentir)\n'
				elif self.hasItem(j,items.robe):
					ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78 (Mentir)\n'
				else:
					ret_str = ret_str+'> Subir **1** Blessure \U0001FA78 (Mentir)\n'
			elif not self.isHunter(j):
				ret_str = ret_str+'> Rien ne se passe \u274C\n'
			elif self.playerlist[j].wounds > 0:
				ret_str = ret_str+'> Soigner **1** Blessure \U0001F489\n'
			elif self.hasGregorShield(j):
				ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
			elif self.hasItem(j,items.robe):
				ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
			else:
				ret_str = ret_str+'> Subir **1** Blessure \U0001FA78\n'
			return ret_str
		elif self.current_vision == vision.lugubre:
			ret_str = ''
			if self.getCharacter(j) == character_list.metamorph:
				if self.playerlist[j].wounds > 0:
					ret_str = ret_str+'> Soigner **1** Blessure \U0001F489\n'
				elif self.hasItem(j,items.robe):
					ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
				else:
					ret_str = ret_str+'> Subir **1** Blessure \U0001FA78\n'
				ret_str = ret_str+'> Rien ne se passe \u274C\n'
			elif not self.isShadow(j):
				ret_str = ret_str+'> Rien ne se passe \u274C\n'
			elif self.playerlist[j].wounds > 0:
				ret_str = ret_str+'> Soigner **1** Blessure \U0001F489\n'
			elif self.hasGregorShield(j):
				ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
			elif self.hasItem(j,items.robe):
				ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
			else:
				ret_str = ret_str+'> Subir **1** Blessure \U0001FA78\n'
			return ret_str
		elif self.current_vision == vision.reconfortante:
			ret_str = ''
			if self.getCharacter(j) == character_list.metamorph:
				ret_str = ret_str+'> Rien ne se passe \u274C\n'
				if self.playerlist[j].wounds > 0:
					ret_str = ret_str+'> Soigner **1** Blessure \U0001F489 (Mentir)\n'
				elif self.hasItem(j,items.robe):
					ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78 (Mentir)\n'
				else:
					ret_str = ret_str+'> Subir **1** Blessure \U0001FA78 (Mentir)\n'
			elif not self.isNeutral(j):
				ret_str = ret_str+'> Rien ne se passe \u274C\n'
			elif self.playerlist[j].wounds > 0:
				ret_str = ret_str+'> Soigner **1** Blessure \U0001F489\n'
			elif self.hasGregorShield(j):
				ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
			elif self.hasItem(j,items.robe):
				ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
			else:
				ret_str = ret_str+'> Subir **1** Blessure \U0001FA78\n'
			return ret_str
		elif self.current_vision == vision.clairvoyante:
			ret_str = ''
			if self.getCharacter(j) == character_list.metamorph:
				if self.hasItem(j,items.robe):
					ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
				else:
					ret_str = ret_str+'> Subir **1** Blessure \U0001FA78\n'
				ret_str = ret_str+'> Rien ne se passe \u274C (Mentir)\n'
			elif not ((self.getCharacter(j)).getHP() <= 11):
				ret_str = ret_str+'> Rien ne se passe \u274C\n'
			elif self.hasGregorShield(j):
				ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
			elif self.hasItem(j,items.robe):
				ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
			else:
				ret_str = ret_str+'> Subir **1** Blessure \U0001FA78\n'
			return ret_str
		elif self.current_vision == vision.destructrice:
			ret_str = ''
			if self.getCharacter(j) == character_list.metamorph:
				ret_str = ret_str+'> Rien ne se passe \u274C\n'
				if self.hasItem(j,items.robe):
					ret_str = ret_str+'> Subir **1** Blessure (Absorbé : 1) \U0001F4A3 (Mentir)\n'
				else:
					ret_str = ret_str+'> Subir **2** Blessures \U0001F4A3 (Mentir)\n'
			elif not ((self.getCharacter(j)).getHP() >= 12):
				ret_str = ret_str+'> Rien ne se passe \u274C\n'
			elif self.hasGregorShield(j):
				ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 2) \U0001F4A3\n'
			elif self.hasItem(j,items.robe):
				ret_str = ret_str+'> Subir **1** Blessure (Absorbé : 2) \U0001F4A3\n'
			else:
				ret_str = ret_str+'> Subir **2** Blessure \U0001F4A3\n'
			return ret_str
		elif self.current_vision == vision.furtive:
			ret_str = ''
			if self.getCharacter(j) == character_list.metamorph:
				if self.hasItem(j,items.robe):
					ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
					ret_str = ret_str + gear_str
				else:
					ret_str = ret_str+'> Subir **1** Blessure \U0001FA78\n'
					ret_str = ret_str + gear_str
				ret_str = ret_str+'> Rien ne se passe \u274C (Mentir)\n'
			elif not (self.isHunter(j) or self.isShadow(j)):
				ret_str = ret_str+'> Rien ne se passe \u274C\n'
			elif self.hasGregorShield(j):
				ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
				ret_str = ret_str + gear_str
			elif self.hasItem(j,items.robe):
				ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
				ret_str = ret_str + gear_str
			else:
				ret_str = ret_str+'> Subir **1** Blessure \U0001FA78\n'
				ret_str = ret_str + gear_str
			return ret_str
		elif self.current_vision == vision.enivrante:
			ret_str = ''
			if self.getCharacter(j) == character_list.metamorph:
				ret_str = ret_str+'> Rien ne se passe \u274C\n'
				if self.hasItem(j,items.robe):
					ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78 (Mentir)\n'
					ret_str = ret_str + gear_str_lie
				else:
					ret_str = ret_str+'> Subir **1** Blessure \U0001FA78 (Mentir)\n'
					ret_str = ret_str + gear_str_lie
			elif not (self.isHunter(j) or self.isNeutral(j)):
				ret_str = ret_str+'> Rien ne se passe \u274C\n'
			elif self.hasGregorShield(j):
				ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
				ret_str = ret_str + gear_str
			elif self.hasItem(j,items.robe):
				ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
				ret_str = ret_str + gear_str
			else:
				ret_str = ret_str+'> Subir **1** Blessure \U0001FA78\n'
				ret_str = ret_str + gear_str
			return ret_str
		elif self.current_vision == vision.cupide:
			ret_str = ''
			if self.getCharacter(j) == character_list.metamorph:
				if self.hasItem(j,items.robe):
					ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
					ret_str = ret_str + gear_str
				else:
					ret_str = ret_str+'> Subir **1** Blessure \U0001FA78\n'
					ret_str = ret_str + gear_str
				ret_str = ret_str+'> Rien ne se passe \u274C (Mentir)\n'
			elif not (self.isShadow(j) or self.isNeutral(j)):
				ret_str = ret_str+'> Rien ne se passe \u274C\n'
			elif self.hasGregorShield(j):
				ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
				ret_str = ret_str + gear_str
			elif self.hasItem(j,items.robe):
				ret_str = ret_str+'> Subir **0** Blessure (Absorbé : 1) \U0001FA78\n'
				ret_str = ret_str + gear_str
			else:
				ret_str = ret_str+'> Subir **1** Blessure \U0001FA78\n'
				ret_str = ret_str + gear_str
			return ret_str
		elif self.current_vision == vision.supreme:
			return '> Lui montrer mon rôle \u27A1'

	# Add all reaction options of player j when receiving the card stored in self.current_vision
	async def react_vision_options(self,message,j):
		if self.current_vision == vision.mortifere:
			if self.getCharacter(j) == character_list.metamorph:
				await message.add_reaction('\u274C')
				await message.add_reaction('\U0001FA78')
			elif not self.isHunter(j):
				await message.add_reaction('\u274C')
			else:
				await message.add_reaction('\U0001FA78')
		elif self.current_vision == vision.foudroyante:
			if self.getCharacter(j) == character_list.metamorph:
				await message.add_reaction('\U0001FA78')
				await message.add_reaction('\u274C')
			elif not self.isShadow(j):
				await message.add_reaction('\u274C')
			else:
				await message.add_reaction('\U0001FA78')
		elif self.current_vision == vision.purificatrice:
			if self.getCharacter(j) == character_list.metamorph:
				await message.add_reaction('\U0001F4A3')
				await message.add_reaction('\u274C')
			elif not self.isShadow(j):
				await message.add_reaction('\u274C')
			else:
				await message.add_reaction('\U0001F4A3')
		elif self.current_vision == vision.divine:
			ret_str = ''
			if self.getCharacter(j) == character_list.metamorph:
				await message.add_reaction('\u274C')
				if self.playerlist[j].wounds > 0:
					await message.add_reaction('\U0001F489')
				else:
					await message.add_reaction('\U0001FA78')
			elif not self.isHunter(j):
				await message.add_reaction('\u274C')
			elif self.playerlist[j].wounds > 0:
				await message.add_reaction('\U0001F489')
			else:
				await message.add_reaction('\U0001FA78')
		elif self.current_vision == vision.lugubre:
			ret_str = ''
			if self.getCharacter(j) == character_list.metamorph:
				if self.playerlist[j].wounds > 0:
					await message.add_reaction('\U0001F489')
				else:
					await message.add_reaction('\U0001FA78')
				await message.add_reaction('\u274C')
			elif not self.isShadow(j):
				await message.add_reaction('\u274C')
			elif self.playerlist[j].wounds > 0:
				await message.add_reaction('\U0001F489')
			else:
				await message.add_reaction('\U0001FA78')
		elif self.current_vision == vision.reconfortante:
			ret_str = ''
			if self.getCharacter(j) == character_list.metamorph:
				await message.add_reaction('\u274C')
				if self.playerlist[j].wounds > 0:
					await message.add_reaction('\U0001F489')
				else:
					await message.add_reaction('\U0001FA78')
			elif not self.isNeutral(j):
				await message.add_reaction('\u274C')
			elif self.playerlist[j].wounds > 0:
				await message.add_reaction('\U0001F489')
			else:
				await message.add_reaction('\U0001FA78')
		elif self.current_vision == vision.clairvoyante:
			if self.getCharacter(j) == character_list.metamorph:
				await message.add_reaction('\U0001FA78')
				await message.add_reaction('\u274C')
			elif not( (self.getCharacter(j)).getHP() <= 11):
				await message.add_reaction('\u274C')
			else:
				await message.add_reaction('\U0001FA78')
		elif self.current_vision == vision.destructrice:
			ret_str = ''
			if self.getCharacter(j) == character_list.metamorph:
				await message.add_reaction('\u274C')
				await message.add_reaction('\U0001F4A3')
			elif not ((self.getCharacter(j)).getHP() >= 12):
				await message.add_reaction('\u274C')
			else:
				await message.add_reaction('\U0001F4A3')
		elif self.current_vision == vision.furtive:
			if self.getCharacter(j) == character_list.metamorph:
				await message.add_reaction('\U0001FA78')
				for k in range(0,len(self.lightInventory(j))):
					await message.add_reaction(((self.lightInventory(j))[k]).getEmoji())
				for k in range(0,len(self.darknessInventory(j))):
					await message.add_reaction(((self.darknessInventory(j))[k]).getEmoji())
				await message.add_reaction('\u274C')
			elif not (self.isHunter(j) or self.isShadow(j)):
				await message.add_reaction('\u274C')
			else:
				await message.add_reaction('\U0001FA78')
				for k in range(0,len(self.lightInventory(j))):
					await message.add_reaction(((self.lightInventory(j))[k]).getEmoji())
				for k in range(0,len(self.darknessInventory(j))):
					await message.add_reaction(((self.darknessInventory(j))[k]).getEmoji())
		elif self.current_vision == vision.enivrante:
			if self.getCharacter(j) == character_list.metamorph:
				await message.add_reaction('\u274C')
				await message.add_reaction('\U0001FA78')
				for k in range(0,len(self.lightInventory(j))):
					await message.add_reaction(((self.lightInventory(j))[k]).getEmoji())
				for k in range(0,len(self.darknessInventory(j))):
					await message.add_reaction(((self.darknessInventory(j))[k]).getEmoji())
			elif not (self.isHunter(j) or self.isNeutral(j)):
				await message.add_reaction('\u274C')
			else:
				await message.add_reaction('\U0001FA78')
				for k in range(0,len(self.lightInventory(j))):
					await message.add_reaction(((self.lightInventory(j))[k]).getEmoji())
				for k in range(0,len(self.darknessInventory(j))):
					await message.add_reaction(((self.darknessInventory(j))[k]).getEmoji())
		elif self.current_vision == vision.cupide:
			if self.getCharacter(j) == character_list.metamorph:
				await message.add_reaction('\U0001FA78')
				for k in range(0,len(self.lightInventory(j))):
					await message.add_reaction(((self.lightInventory(j))[k]).getEmoji())
				for k in range(0,len(self.darknessInventory(j))):
					await message.add_reaction(((self.darknessInventory(j))[k]).getEmoji())
				await message.add_reaction('\u274C')
			elif not (self.isNeutral(j) or self.isShadow(j)):
				await message.add_reaction('\u274C')
			else:
				await message.add_reaction('\U0001FA78')
				for k in range(0,len(self.lightInventory(j))):
					await message.add_reaction(((self.lightInventory(j))[k]).getEmoji())
				for k in range(0,len(self.darknessInventory(j))):
					await message.add_reaction(((self.darknessInventory(j))[k]).getEmoji())
		elif self.current_vision == vision.supreme:
			await message.add_reaction('\u27A1')
		
	## Print targets
	# 0 No specific indication
	# 1 Normal attack
	# 2 Voodoo doll
	# 3 Bat, Spider
	# 4 Haunted Forest
	# 5 Vision
	# 6 Majora's Wrath
	# 7 Mummy's Power
	# 8 Erik's healing
	def print_targets(self,include_self,source):

		# Getting locations ID
		id_of_player_loc = self.getLocationId(self.getLocation(self.turn_of))
		id_of_twin_loc = self.getIdOfTwinLocation(id_of_player_loc)
		id_of_nearby_loc = self.getIdOfOtherNearbyLocation(id_of_player_loc)

		ret_str = ''
		for j in range(0,self.nb_players()):
			if self.isAlive(j) and (((j == self.turn_of) and include_self) or j != self.turn_of):

				no_bow_condition = (self.getLocation(j) == self.gamemap[id_of_player_loc] or self.getLocation(j) == self.gamemap[id_of_twin_loc]) and not self.hasItem(self.turn_of,items.bow)
				away_condition = (self.getLocation(j) != self.gamemap[id_of_player_loc] and self.getLocation(j) != self.gamemap[id_of_twin_loc])
				bow_condition = away_condition and self.hasItem(self.turn_of,items.bow)
				tipper_condition = self.getLocation(j) == self.gamemap[id_of_twin_loc] or self.getLocation(j) == self.gamemap[id_of_nearby_loc]

				if source == 8 and (not away_condition):
					ret_str = ret_str+'> '+self.getName(j)+' '+str(self.getEmoji(j))+'\n'

				if source == 7 and self.getLocation(j) == location.otherworld_door:
					ret_str = ret_str+'> '+str(self.getEmoji(j))+' : **Infliger 3 Blessures** à '+self.getName(j)+' '+str(self.getEmoji(j))
					if self.hasGregorShield(j):
						ret_str = ret_str+' (Insensible)'
					elif self.hasItem(j,items.robe) or (j == self.neo_id and self.turn_of == self.neo_target):
						ret_str = ret_str+' (-1)'
					ret_str = ret_str+' (puis te déplacer)\n'

				if source == 6 and away_condition:
					ret_str = ret_str+'> '+self.getName(j)+' '+str(self.getEmoji(j))
					if self.hasGregorShield(j):
						ret_str = ret_str+' (Insensible)'
					elif self.hasItem(j,items.robe) or (j == self.neo_id and self.turn_of == self.neo_target):
						ret_str = ret_str+' (-1)'
					ret_str = ret_str+'\n'

				if source == 5:
					ret_str = ret_str+'> '+self.getName(j)+' '+str(self.getEmoji(j))
					if self.hasGregorShield(j):
						ret_str = ret_str+' (Insensible aux dégâts)'
					elif self.hasItem(j,items.robe) or (j == self.neo_id and self.turn_of == self.neo_target):
						ret_str = ret_str+' (-1 aux Blessures subies)'
					ret_str = ret_str+'\n'

				elif source == 4:
					ret_str = ret_str+'> '+self.getName(j)+' '+str(self.getEmoji(j))
					if self.hasGregorShield(j) or self.hasItem(j,items.pin):
						ret_str = ret_str+' (Insensible aux dégâts)'
					elif self.hasItem(j,items.robe) or (j == self.neo_id and self.turn_of == self.neo_target):
						ret_str = ret_str+' (-1)'
					ret_str = ret_str+'\n'

				elif source == 3:
					ret_str = ret_str+'> '+self.getName(j)+' '+str(self.getEmoji(j))
					if self.hasItem(j,items.amulet) or self.hasGregorShield(j):
						ret_str = ret_str+' (Insensible)'
					elif self.hasItem(j,items.robe) or (j == self.neo_id and self.turn_of == self.neo_target):
						ret_str = ret_str+' (-1)'
					ret_str = ret_str+'\n'

				elif source == 2:
					ret_str = ret_str+'> '+self.getName(j)+' '+str(self.getEmoji(j))
					if self.hasGregorShield(j):
						ret_str = ret_str+' (Insensible)'
					elif self.hasItem(j,items.robe) or (j == self.neo_id and self.turn_of == self.neo_target):
						ret_str = ret_str+' (-1)'
					ret_str = ret_str+'\n'

				elif source == 1 and ( bow_condition or no_bow_condition ):
					ret_str = ret_str+'> '+self.getName(j)+' '+str(self.getEmoji(j))

					bonus = 0
					if self.spearAvailable(self.turn_of):
						bonus = bonus+2
					if self.hasItem(self.turn_of,items.robe):
						bonus = bonus-1
					if self.hasAura(j) or self.hasItem(j,items.robe) or (j == self.neo_id and self.turn_of == self.neo_target):
						bonus = bonus-1
					if self.hasItem(self.turn_of,items.axe):
						bonus = bonus+1
					if self.hasItem(self.turn_of,items.zweihander):
						bonus = bonus+1
					if self.hasItem(self.turn_of,items.mace):
						bonus = bonus+1
					if self.getCharacter(self.turn_of) == character_list.marth and self.isRevealed(self.turn_of) and self.isAbilityAvailable(self.turn_of) and tipper_condition:
							bonus = bonus+1
					if self.getCharacter(self.turn_of) == character_list.ganondorf and self.isRevealed(self.turn_of) and self.isAbilityAvailable(self.turn_of):
						bonus = bonus + len(self.darknessInventory(self.turn_of))
						if bonus > 3:
							bonus = 3
					plus = ''
					if bonus > 0:
						plus = '+'


					if self.hasGuardianAngel(j) or self.hasGregorShield(j):
						ret_str = ret_str + ' (Insensible)'
					else:
						if bonus != 0:
							ret_str = ret_str + ' ('+plus+str(bonus)+')'
						# Link can try to block
						if self.getCharacter(j) == character_list.link and self.isRevealed(j) and self.isAbilityAvailable(j):
							ret_str = ret_str + ' (Blocable)'
					ret_str = ret_str+'\n'

				elif source == 0:
					ret_str = ret_str+'> '+self.getName(j)+' '+str(self.getEmoji(j))
					ret_str = ret_str+'\n'
		return ret_str

	## Add target reactions to message
	# 0 No specific indication
	# 1 Normal attack
	# 2 Mummy's Power
	# 3 Erik's Healing
	async def print_target_reactions(self,message,include_self,source):

		# Getting locations ID
		id_of_player_loc = self.getLocationId(self.getLocation(self.turn_of))
		id_of_twin_loc = self.getIdOfTwinLocation(id_of_player_loc)

		for j in range(0,self.nb_players()):
			if self.isAlive(j) and (((j == self.turn_of) and include_self) or j != self.turn_of):

				away_condition = (self.getLocation(j) != self.gamemap[id_of_player_loc] and self.getLocation(j) != self.gamemap[id_of_twin_loc])

				no_bow_condition = (self.getLocation(j) == self.gamemap[id_of_player_loc] or self.getLocation(j) == self.gamemap[id_of_twin_loc]) and not self.hasItem(self.turn_of,items.bow)
				bow_condition = self.getLocation(j) != self.gamemap[id_of_player_loc] and self.getLocation(j) != self.gamemap[id_of_twin_loc] and self.hasItem(self.turn_of,items.bow)


				if source == 3 and (not away_condition):
					await message.add_reaction(self.getEmoji(j))

				if source == 2 and self.getLocation(j) == location.otherworld_door:
					await message.add_reaction(self.getEmoji(j))

				if source == 1 and ( bow_condition or no_bow_condition ):
					await message.add_reaction(self.getEmoji(j))

				elif source == 0:
					await message.add_reaction(self.getEmoji(j))

	## Healing a player
	# 0 full heal
	# 1 haunted forest
	# 2 holy water
	# 3 benediction
	# 4 Vampire Bat
	# 5 Ring
	# 6 Vision
	# 7 Vampire
	# 8 Catherine
	# 9 Erik
	def heal(self,pid1,pid2,value,source):
		ret_string = ''

		# If the player benefits from a full heal
		if source == 0:
			ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' regagne toute sa vie.\n' 
			self.playerlist[pid2].heal(value)

		# If the player is under the Haunted Forest effect
		if source == 1:
			ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' invoque les esprits de la Forêt Hantée pour soigner **'+str(value)+'** Blessure à **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+'.\n' 
			self.playerlist[pid2].heal(value)

		# Holy water
		if source == 2 and pid1 == pid2:
			ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' se soigne **'+str(value)+'** Blessures grâce à l\'Eau bénite.\n' 
			self.playerlist[pid2].heal(value)

		# If the player is using the Benediction
		if source == 3:
			ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' utilise la Bénédiction pour soigner **'+str(value)+'** Blessures à **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+'.\n' 
			self.playerlist[pid2].heal(value)

		# If the player is using the Vampire Bat
		if source == 4 and pid1 == pid2:
			ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' se soigne **'+str(value)+'** Blessure.\n' 
			self.playerlist[pid2].heal(value)

		# If the player is using the Ring
		if source == 5 and pid1 == pid2:
			ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' se soigne **'+str(value)+'** Blessure grâce à la Bague \U0001F48D.\n' 
			self.playerlist[pid2].heal(value)

		# Vision
		if source == 6:
			ret_string = self.getName(pid2)+' '+str(self.getEmoji(pid2))+' se soigne **'+str(value)+'** Blessure.\n' 
			self.playerlist[pid2].heal(value)

		# Vampire
		if source == 7:
			ret_string = self.getName(pid2)+' '+str(self.getEmoji(pid2))+' se soigne **'+str(value)+'** Blessure.\n' 
			self.playerlist[pid2].heal(value)

		# Catherine
		if source == 8:
			ret_string = self.getName(pid2)+' '+str(self.getEmoji(pid2))+' se soigne **'+str(value)+'** Blessure.\n' 
			self.playerlist[pid2].heal(value)

		# Erik
		if source == 9:
			if pid1 == pid2:
				ret_string = self.getName(pid2)+' '+str(self.getEmoji(pid2))+' se soigne **'+str(value)+'** Blessures.\n' 
				self.playerlist[pid2].heal(value)
			else:
				ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' soigne **'+str(value)+'** Blessures à **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+'.\n' 
				self.playerlist[pid2].heal(value)

		return ret_string

	## Dealing damage to a player.
	# Source :
	# -1 : suicide
	# 0 for a simple attack at the end of a turn
	# 1 haunted forest
	# 2 divine lightning or Franklin's power
	# 3 First Aid/Fu-Ka's Power
	# 4 Vampire Bat
	# 5 Spider
	# 6 Dynamite
	# 7 Voodoo doll
	# 8 Banana peel
	# 9 AIDS
	# 10 Vision
	# 11 Blocked by Link
	# 12 Majora
	# 13 Mograine's 2nd attack
	# 14 Mograine's 2nd attack blocked by Link
	# 15 Werewolf's counterattack
	# 16 Werewolf's counterattack blocked by Link
	def damage(self,pid1,pid2,value,source):
		ret_string = ''
		temp = ''
		original_HP = self.playerlist[pid2].wounds

		# Getting locations ID
		id_of_player_loc = self.getLocationId(self.getLocation(pid1))
		id_of_twin_loc = self.getIdOfTwinLocation(id_of_player_loc)
		id_of_nearby_loc = self.getIdOfOtherNearbyLocation(id_of_player_loc)
		tipper_condition = self.getLocation(pid2) == self.gamemap[id_of_twin_loc] or self.getLocation(pid2) == self.gamemap[id_of_nearby_loc]

		# If the player commits suicide ; provided that "value" is big enough
		if source == -1 and pid1 == pid2:
			ret_string = self.getName(pid2)+' '+str(self.getEmoji(pid2))+' **se suicide**.\n' 
			temp = self.playerlist[pid2].damage(value)

		# If the player is simply attacked
		if source == 0 or source == 11 or source == 13 or source == 14 or source == 15 or source == 16:
			new_value = value
			if self.spearAvailable(pid1) and value != 0 and source != 15 and source != 16:
				new_value = new_value+2
			if self.hasItem(pid1,items.axe) and value != 0 and source != 15 and source != 16:
				new_value = new_value+1
			if self.hasItem(pid1,items.zweihander) and value != 0 and source != 15 and source != 16:
				new_value = new_value+1
			if self.hasItem(pid1,items.mace) and value != 0 and source != 15 and source != 16:
				new_value = new_value+1
			if self.hasItem(pid1,items.robe) and value != 0 and source != 15 and source != 16:
				new_value = new_value-1
			if self.getCharacter(self.turn_of) == character_list.marth and self.isRevealed(self.turn_of) and self.isAbilityAvailable(self.turn_of) and tipper_condition and value != 0:
				new_value = new_value+1
			if self.getCharacter(self.turn_of) == character_list.ganondorf and self.isRevealed(self.turn_of) and self.isAbilityAvailable(self.turn_of) and value != 0:
				new_value = new_value + len(self.darknessInventory(self.turn_of))
				if new_value-value > 3:
					new_value = value+3

			if source == 13 or source == 14:
				new_value = new_value//2

			# Vanilla attack
			if source != 15 and source != 16:
				if self.hasGuardianAngel(pid2) or self.hasGregorShield(pid2) or source == 11 or source == 14:
					ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' attaque **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **0** Blessure (Absorbé : '+str(new_value)+').\n' 
				elif (self.hasItem(pid2,items.robe) or self.hasAura(pid2) or (pid2 == self.neo_id and pid1 == self.neo_target)) and new_value > 0:
					ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' attaque **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **'+str(new_value-1)+'** Blessures (Absorbé : 1).\n' 
					temp = self.playerlist[pid2].damage(new_value-1)
				else:
					ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' attaque **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **'+str(new_value)+'** Blessures.\n' 
					temp = self.playerlist[pid2].damage(new_value)

			# Werewolf counterattack
			else:
				if self.hasGuardianAngel(pid2) or self.hasGregorShield(pid2) or source == 16:
					ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' contre-attaque **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **0** Blessure (Absorbé : '+str(new_value)+').\n' 
				elif (self.hasItem(pid2,items.robe) or self.hasAura(pid2) or (pid2 == self.neo_id and pid1 == self.neo_target)) and new_value > 0:
					ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' contre-attaque **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **'+str(new_value-1)+'** Blessures (Absorbé : 1).\n' 
					temp = self.playerlist[pid2].damage(new_value-1)
				else:
					ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' contre-attaque **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **'+str(new_value)+'** Blessures.\n' 
					temp = self.playerlist[pid2].damage(new_value)

		# If the player is under the Haunted Forest effect
		if source == 1:
			if self.hasItem(pid2,items.pin) or self.hasGregorShield(pid2):
				ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' maudit **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **0** Blessure (Absorbé : 2).\n' 
			elif self.hasItem(pid2,items.robe) or (pid2 == self.neo_id and pid1 == self.neo_target):
				ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' maudit **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **'+str(value-1)+'** Blessures (Absorbé : 1).\n' 
				temp = self.playerlist[pid2].damage(value-1)
			else:
				ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' maudit **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **'+str(value)+'** Blessures.\n' 
				temp = self.playerlist[pid2].damage(value)

		# Lightning
		if source == 2:
			if self.hasGregorShield(pid2):
				ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' foudroie **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **0** Blessure (Absorbé : 2).\n' 
			elif self.hasItem(pid2,items.robe) or (pid2 == self.neo_id and pid1 == self.neo_target):
				ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' foudroie **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **'+str(value-1)+'** Blessures (Absorbé : 1).\n' 
				temp = self.playerlist[pid2].damage(value-1)
			else:
				ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' foudroie **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **'+str(value)+'** Blessures.\n' 
				temp = self.playerlist[pid2].damage(value)

		# First Aid/Fu-Ka's Power
		if source == 3:
			ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' place **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' à **7** Blessures.\n' 
			self.playerlist[pid2].wounds = 7

		# Vampire Bat
		if source == 4:
			if self.hasItem(pid2,items.amulet) or self.hasGregorShield(pid2):
				ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' vampirise **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **0** Blessure (Absorbé : 2).\n' 
			elif self.hasItem(pid2,items.robe) or (pid2 == self.neo_id and pid1 == self.neo_target):
				ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' vampirise **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **'+str(value-1)+'** Blessures (Absorbé : 1).\n' 
				temp = self.playerlist[pid2].damage(value-1)
			else:
				ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' vampirise **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **'+str(value)+'** Blessures.\n' 
				temp = self.playerlist[pid2].damage(value)

		# Spider
		if source == 5:
			if self.hasItem(pid2,items.amulet) or self.hasGregorShield(pid2):
				ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' infeste **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **0** Blessure (Absorbé : 2).\n' 
			elif self.hasItem(pid2,items.robe) or (pid2 == self.neo_id and pid1 == self.neo_target):
				ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' infeste **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **'+str(value-1)+'** Blessures (Absorbé : 1).\n' 
				temp = self.playerlist[pid2].damage(value-1)
			else:
				ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' infeste **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **'+str(value)+'** Blessures.\n' 
				temp = self.playerlist[pid2].damage(value)

		# Dynamite
		if source == 6:
			if self.hasItem(pid2,items.amulet) or self.hasGregorShield(pid2):
				ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' explose **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **0** Blessure (Absorbé : 3).\n' 
			elif self.hasItem(pid2,items.robe) or (pid2 == self.neo_id and pid1 == self.neo_target):
				ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' explose **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **'+str(value-1)+'** Blessures (Absorbé : 1).\n' 
				temp = self.playerlist[pid2].damage(value-1)
			else:
				ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' explose **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **'+str(value)+'** Blessures.\n' 
				temp = self.playerlist[pid2].damage(value)

		# Voodoo Doll
		if source == 7:
			if self.hasGregorShield(pid2):
				ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' maudit **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **0** Blessure (Absorbé : 3).\n' 
			elif self.hasItem(pid2,items.robe) or (pid2 == self.neo_id and pid1 == self.neo_target):
				ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' maudit **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **'+str(value-1)+'** Blessures (Absorbé : 1).\n' 
				temp = self.playerlist[pid2].damage(value-1)
			else:
				ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' maudit **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **'+str(value)+'** Blessures.\n' 
				temp = self.playerlist[pid2].damage(value)

		# Banana Peel
		if source == 8 and pid1 == pid2:
			if self.hasGregorShield(pid2):
				ret_string = self.getName(pid2)+' '+str(self.getEmoji(pid2))+' glisse et subit **0** Blessure (Absorbé : 1).\n' 
			elif self.hasItem(pid2,items.robe):
				ret_string = self.getName(pid2)+' '+str(self.getEmoji(pid2))+' glisse et subit **'+str(value-1)+'** Blessure (Absorbé : 1).\n' 
				temp = self.playerlist[pid2].damage(value-1)
			else:
				ret_string = self.getName(pid2)+' '+str(self.getEmoji(pid2))+' glisse et subit **'+str(value)+'** Blessure.\n' 
				temp = self.playerlist[pid2].damage(value)

		# AIDS
		if source == 9:
			if pid1 == pid2:
				if self.hasGregorShield(pid2):
					ret_string = self.getName(pid2)+' '+str(self.getEmoji(pid2))+' est maudit par l\'Idole \U0001F5FF et subit **0** Blessure (Absorbé : 1).\n' 
				elif self.hasItem(pid2,items.robe):
					ret_string = self.getName(pid2)+' '+str(self.getEmoji(pid2))+' est maudit par l\'Idole \U0001F5FF et subit **'+str(value-1)+'** Blessure (Absorbé : 1).\n' 
					temp = self.playerlist[pid2].damage(value-1)
				else:
					ret_string = self.getName(pid2)+' '+str(self.getEmoji(pid2))+' est maudit par l\'Idole \U0001F5FF et subit **'+str(value)+'** Blessure.\n' 
					temp = self.playerlist[pid2].damage(value)
			else:
				if self.hasGregorShield(pid2):
					ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' maudit **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' avec l\'Idole \U0001F5FF et lui inflige **0** Blessure (Absorbé : 1).\n'
				elif self.hasItem(pid2,items.robe) or (pid2 == self.neo_id and pid1 == self.neo_target):
					ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' maudit **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' avec l\'Idole \U0001F5FF et lui inflige **'+str(value-1)+'** Blessures (Absorbé : 1).\n' 
					temp = self.playerlist[pid2].damage(value-1)
				else:
					ret_string = self.getName(pid1)+' '+str(self.getEmoji(pid1))+' maudit **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' avec l\'Idole \U0001F5FF et lui inflige **'+str(value)+'** Blessures.\n' 
					temp = self.playerlist[pid2].damage(value)

		# Vision
		if source == 10:
			if self.hasGregorShield(pid2):
				ret_string = self.getName(pid2)+' '+str(self.getEmoji(pid2))+' subit **0** Blessure (Absorbé : '+str(value)+').\n' 
			elif self.hasItem(pid2,items.robe) or (pid2 == self.neo_id and pid1 == self.neo_target):
				ret_string = self.getName(pid2)+' '+str(self.getEmoji(pid2))+' subit **'+str(value-1)+'** Blessure (Absorbé : 1).\n' 
				temp = self.playerlist[pid2].damage(value-1)
			else:
				ret_string = self.getName(pid2)+' '+str(self.getEmoji(pid2))+' subit **'+str(value)+'** Blessure.\n' 
				temp = self.playerlist[pid2].damage(value)

		# Majora
		if source == 12:
			if self.hasGregorShield(pid2):
				ret_string = 'Une pluie de roches lunaires s\'abat sur **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **0** Blessure (Absorbé : 2).\n' 
			elif self.hasItem(pid2,items.robe) or (pid2 == self.neo_id and pid1 == self.neo_target):
				ret_string = 'Une pluie de roches lunaires s\'abat sur **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **'+str(value-1)+'** Blessures (Absorbé : 1).\n' 
				temp = self.playerlist[pid2].damage(value-1)
			else:
				ret_string = 'Une pluie de roches lunaires s\'abat sur **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+' et lui inflige **'+str(value)+'** Blessures.\n' 
				temp = self.playerlist[pid2].damage(value)

		# Awakening from the slumber
		new_HP = self.playerlist[pid2].wounds
		if self.isAlive(pid2) and self.getSleepTime(pid2) > 0 and new_HP > original_HP:
			self.setSleepTime(pid2,0)
			temp = temp+self.getName(pid2)+' '+str(self.getEmoji(pid2))+' **se réveille**.'

		# If the player died
		if (not self.isAlive(pid2)):
			if source != -1:
				if pid1 == pid2:
					ret_string = ret_string + self.getName(pid1)+' '+str(self.getEmoji(pid1))+' a succombé.\n'
				else:
					ret_string = ret_string + self.getName(pid1)+' '+str(self.getEmoji(pid1))+' a tué **'+self.getName(pid2)+'** '+str(self.getEmoji(pid2))+'.\n'
			self.just_died = self.just_died+[pid2]
		else:
			# Triggering the counterattack if possible
			if pid2 == self.werewolf_id and self.isAbilityAvailable(pid2) and self.isRevealed(pid2) and (source == 0 or source == 13):
				self.counterattack_available = True

		return ret_string+temp
			

