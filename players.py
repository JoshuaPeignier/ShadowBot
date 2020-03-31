import characters
import exceptions
import location

class Player:
	discorduser=None
	emoji=None
	character=None
	revealed=False
	current_location=None
	wounds=0

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
		return self.discorduser.name

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

	def isRevealed(self):
		return self.revealed

	def getLocation(self):
		return self.current_location

	def getWounds(self):
		return self.wounds


	## Some modifiers
	def setEmoji(self,emo):
		self.emoji = emo

	def setCharacter(self,character):
		self.character = character

	def reveals(self):
		if (not self.isRevealed()):
			self.revealed = True
			return self.mention()+' '+str(self.emoji)+' révèle son identité : '+self.getCharNameColor()
		else:
			raise exceptions.AlreadyRevealed

	def setLocation(self,location):
		self.current_location = location

	##
	def mention(self):
		return self.discorduser.mention
