class Character:
	name=None
	totalHealth=0
	faction=None
	color=''
	wincon=None
	abilityText=None
	uniqueUse=False
	choice=False

	## Initialisation of the character
	def __init__(self,name_of,health,team,color,winconText,abText,uniqueUse,choice):
		self.name = name_of
		self.totalHealth = health
		self.faction = team
		self.color = color
		self.wincon = winconText
		self.abilityText = abText
		self.uniqueUse = uniqueUse
		self.choice = choice

	## Comparison of characters
	def __eq__(self,other):
		if isinstance(other,self.__class__):
			return (self.name==other.name)
		else:
			return False

	def __ne__(self,other):
		return not self.__eq__(other)

	## Obtaining basic information
	def getName(self):
		return self.name

	def getNameColor(self):
		return self.name+' '+self.color

	def getHP(self):
		return self.totalHealth

	def getFaction(self):
		return self.faction

	def getColor(self):
		return self.color

	def getWincon(self):
		return self.wincon

	def getAbilityText(self):
		return self.abilityText

	def uniqueAbility(self):
		return self.uniqueUse

	def hasRealAbility(self):
		return self.choice

	def info(self):
		power=""
		if self.choice:
			power = "**Pouvoir** : "
		else:
			power = "**Particularité** : "
		return "**Nom** : "+self.name+"\n**Points de vie** : "+str(self.totalHealth)+"\n**Camp** : "+self.faction+' '+self.color+"\n**Condition de victoire** : "+self.wincon+"\n"+power+self.abilityText+"\n"
