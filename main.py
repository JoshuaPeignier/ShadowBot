import random
import players
import characters
import character_list
import location

class Game:

	# Player parameters
	playerlist=[]
	nb_hunters=0
	nb_shadows=0
	nb_neutrals=0
	char_pool=[]
	gamemap=[]
	turn_of=0

	# Winning conditions parameters
	first_blood = False # While false, Catherine and Daniel can win by dying first.
	agnes_switched = False # Used in the victory condition of Agnes
	neo_target = None # Used in the victory condition of Neo
	neo_revenge_activated = None # While false, Neo only needs to protect the player who plays before her.

	# Cards piles
	light_pile=[]
	light_discarded=[]
	darkness_pile=[]
	darkness_discard=[]
	vision_pile=[]
	vision_discard=[]


	## Initialisation of the game
	def __init__(self,l):

		## Creating the players objects
		newplayer = None
		for i in range(0,len(l)):
			newplayer = players.Player(l[i][0],l[i][1])
			self.playerlist = self.playerlist+[newplayer]
		random.shuffle(self.playerlist)

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
			self.playerlist[i].setCharacter(self.char_pool[i])
		self.char_pool=[]

		## Shuffling the game map
		self.gamemap=location.location_list.copy()
		random.shuffle(self.gamemap)

		## Randomly placing the players
		for i in range(0,len(l)):
			self.playerlist[i].setLocation(random.choice(self.gamemap))

	## Cleans the object
	def clean(self):
		self.playerlist=[]

	## Useful information on the state of the game
	def nb_players(self):
		return len(self.playerlist)

	def players_order_str(self):
		res='Les joueurs jouent dans cet ordre :\n'
		for i in range(0,self.nb_players()):
			res=res+str(i+1)+') '+self.playerlist[i].getName()+' '+str(self.playerlist[i].getEmoji())+'\n'
		return res

	def get_player(self,player):
		for i in range(0,self.nb_players()):
			if self.playerlist[i].getName() == player.name:
				return self.playerlist[i]
		raise exceptions.PlayerNotFound

	def get_players_state(self):
		res=''
		for i in range(0,self.nb_players()):
			res=res+str(i+1)+') '+self.playerlist[i].getName()+' '+str(self.playerlist[i].getEmoji())
			if(i == self.turn_of):
				res=res+' (en train de jouer)'
			res=res+'\n'
			if(self.playerlist[i].isRevealed()):
				res=res+'Personnage : '+self.playerlist[i].getCharNameColor()+'\n'
			res=res+'Blessures : '+str(self.playerlist[i].getWounds())+'/'
			if(self.playerlist[i].isRevealed()):
				res=res+str(self.playerlist[i].getCharacter().getHP())+'\n'
			else:
				res=res+'??\n'
			res=res+'\n'
		return res

	def get_board(self):
		res=''
		for i in range(0,len(self.gamemap)):
			res=res+self.gamemap[i].getNameColor()+' : '
			for j in range(0,len(self.playerlist)):
				if self.playerlist[j].getLocation() == self.gamemap[i]:
					res=res+'\t'+self.playerlist[j].getName()+' '+str(self.playerlist[j].getEmoji())
					if self.playerlist[j].isRevealed():
						res=res+' ('+self.playerlist[j].getCharNameColor()+' )'
			res=res+'\n'
			if i%2 == 1:
				res=res+'\n'
		return res

	def getChannel(self,i):
		return self.playerlist[i].getChannel()

	## Small actions
	def d4(self):
		return random.randint(1,4)

	def d6(self):
		return random.randint(1,6)

	## Some modifiers
	def reveal_all(self):
		res=''
		for i in range(0,self.nb_players()):
			if (not self.playerlist[i].isRevealed()):
				res=res+self.playerlist[i].reveals()+'\n'
		return res

	def reveal_player(self,player):
		return self.get_player(player).reveals()

