import characters
import exceptions
import location
import items

class Player:
	discorduser=None
	emoji=None
	character=None
	revealed=False
	alive=True
	current_location=None
	guardian_angel = False
	wounds = 0
	turns_left = 0
	light_inventory = []
	darkness_inventory = []

	ability_available = True
	aura = False
	gregor_shield = False
	sleep = 0

	## Initialisation of the player
	def __init__(self,user,emo):
		self.discorduser = user
		self.emoji = emo

	## Comparison of players
	def __eq__(self,other):
		if isinstance(other,self.__class__):
			return (self.discorduser==other.discorduser) and (self.emoji==other.emoji)
		else:
			return False

	def __ne__(self,other):
		return not self.__eq__(other)

	## Obtaining basic information
	def getChannel(self):
		return self.discorduser.dm_channel

	def getUser(self):
		return self.discorduser

	def getMention(self):
		return self.discorduser.mention

	def getName(self):
		return self.discorduser.display_name

	def getEmoji(self):
		return self.emoji

	def getCharacter(self):
		return self.character

	def getCharName(self):
		return self.character.getName()

	def getCharNameColor(self):
		return self.character.getNameColor()

	def getCharDescription(self):
		return self.character.info()

	def getFaction(self):
		return self.character.getFaction()

	def isHunter(self):
		return self.character.getFaction() == "Hunter"

	def isShadow(self):
		return self.character.getFaction() == "Shadow"

	def isNeutral(self):
		return self.character.getFaction() == "Neutre"

	def isRevealed(self):
		return self.revealed

	def getLocation(self):
		return self.current_location

	def isAlive(self):
		return self.alive

	def getWounds(self):
		return self.wounds

	def hasGuardianAngel(self):
		return self.guardian_angel

	def isInventoryEmpty(self):
		return (len(self.light_inventory)+len(self.darkness_inventory) == 0)

	def lightInventory(self):
		return self.light_inventory

	def darknessInventory(self):
		return self.darkness_inventory

	def hasItem(self,item):
		for i in range(0, len(self.light_inventory)):
			if self.light_inventory[i] == item:
				return True

		for i in range(0, len(self.darkness_inventory)):
			if self.darkness_inventory[i] == item:
				return True

		return False

	def isAbilityAvailable(self):
		return self.ability_available

	def hasAura(self):
		return self.aura

	def hasGregorShield(self):
		return self.gregor_shield

	def getSleepTime(self):
		return self.sleep

	## Some modifiers
	def setEmoji(self,emo):
		self.emoji = emo

	def setCharacter(self,character):
		self.character = character

	def reveals(self):
		if (not self.isRevealed()):
			self.revealed = True
			return self.getName()+' '+str(self.getEmoji())+' révèle son identité : '+self.getCharNameColor()
		else:
			raise exceptions.AlreadyRevealed

	def setLocation(self,location):
		self.current_location = location

	def damage(self,amount):
		self.wounds = self.wounds+amount
		if (self.wounds >= self.getCharacter().getHP() ):
			self.alive = False
			if (not self.isRevealed()):
				return self.reveals()
			else:
				return ''
		else:
			return ''

	def heal(self,amount):
		self.wounds = self.wounds-amount
		if (self.wounds < 0):
			self.wounds = 0

	def getGuardianAngel(self):
		self.guardian_angel = True

	def loseGuardianAngel(self):
		self.guardian_angel = False

	def gainItem(self,item):
		if item == items.amulet or  item == items.ring or  item == items.compass or  item == items.pin or  item == items.cross or  item == items.spear or  item == items.robe:
			self.light_inventory = self.light_inventory + [item]

		if item == items.bow or  item == items.zweihander or  item == items.axe or  item == items.aids or  item == items.katana or  item == items.mace or  item == items.gunmachine:
			self.darkness_inventory = self.darkness_inventory + [item]


	def loseItem(self,item):
		if item == items.amulet or  item == items.ring or  item == items.compass or  item == items.pin or  item == items.cross or  item == items.spear or  item == items.robe:
			for i in range(0, len(self.light_inventory)):
				if self.light_inventory[i] == item:
					self.light_inventory = self.light_inventory[0:i]+self.light_inventory[i+1:len(self.light_inventory)]
					break

		if item == items.bow or  item == items.zweihander or  item == items.axe or  item == items.aids or  item == items.katana or  item == items.mace or  item == items.gunmachine:
			for i in range(0, len(self.darkness_inventory)):
				if self.darkness_inventory[i] == item:
					self.darkness_inventory = self.darkness_inventory[0:i]+self.darkness_inventory[i+1:len(self.darkness_inventory)]
					break

	def consumeAbility(self):
		self.ability_available = False

	def gainAura(self):
		self.aura = True

	def loseAura(self):
		self.aura = False

	def gainGregorShield(self):
		self.gregor_shield = True

	def loseGregorShield(self):
		self.gregor_shield = False

	def setSleepTime(self,k):
		self.sleep = k

	def decreaseSleepTime(self):
		self.sleep = self.sleep-1

	##
	def mention(self):
		return self.discorduser.mention
