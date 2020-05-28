class Location:
	name = ""
	color = ""
	info = ""

	## Initialisation of the location
	def __init__(self,name,color,info):
		self.name = name
		self.color = color
		self.info = info

	## Comparison of characters
	def __eq__(self,other):
		if isinstance(other,self.__class__):
			return (self.name==other.name)
		else:
			return False

	def __ne__(self,other):
		return not self.__eq__(other)

	## Obtaining name :
	def getName(self):
		return self.name

	def getNameArticle(self):
		if self.name == "Antre de l'Ermite":
			return "l'Antre de l'Ermite"
		elif self.name == "Porte de l'Outremonde":
			return "la Porte de l'Outremonde"
		elif self.name == "Monastère":
			return "le Monastère"
		elif self.name == "Cimetière":
			return "le Cimetière"
		elif self.name == "Forêt Hantée":
			return "la Forêt Hantée"
		elif self.name == "Sanctuaire Ancien":
			return "le Sanctuaire Ancien"

	def getColor(self):
		return self.color

	def getNameColor(self):
		return '**'+self.name+'** '+self.color

	def getInfo(self):
		return self.getNameColor()+' : '+self.info

hermit_lair = Location("Antre de l'Ermite","\U0001F7E9","Vous pouvez piocher une carte vision.")
otherworld_door = Location("Porte de l'Outremonde","\U0001F7EA","Vous pouvez piocher une carte de la couleur de votre choix.")
monastery = Location("Monastère","\u2B1C","Vous pouvez piocher une carte Lumière.")
graveyard = Location("Cimetière","\u2B1B","Vous pouvez piocher une carte Ténèbres.")
haunted_forest = Location("Forêt Hantée","\U0001F7EB","Vous pouvez infliger 2 Blessures au joueur de votre choix, ou soigner une de vos Blessures.")
ancient_sanctuary = Location("Sanctuaire Ancien","\U0001F7E7","Vous pouvez voler une carte équipement au joueur de votre choix.")

location_list = [hermit_lair, otherworld_door, monastery, graveyard, haunted_forest, ancient_sanctuary]

location_dictionary = {
"Antre de l'Ermite": hermit_lair,
"Porte de l'Outremonde": otherworld_door,
"Monastère": monastery,
"Cimetière": graveyard,
"Forêt Hantée": haunted_forest,
"Sanctuaire Ancien": ancient_sanctuary
}
