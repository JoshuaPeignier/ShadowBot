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

	def getNameColor(self):
		return '**'+self.name+'** '+self.color

	def getInfo(self):
		return self.info

hermit_lair = Location("Antre de l'Ermite",":green_square:","Vous pouvez piocher une carte vision.")
otherworld_door = Location("Porte de l'Outremonde",":purple_square:","Vous pouvez piocher une carte de la couleur de votre choix.")
monastery = Location("Monastère",":white_large_square:","Vous pouvez piocher une carte Lumière.")
graveyard = Location("Cimetière",":black_large_square:","Vous pouvez piocher une carte Ténèbres.")
haunted_forest = Location("Forêt Hantée",":brown_square:","Vous pouvez infliger 2 Blessures au joueur de votre choix, ou soigner une de vos Blessures.")
ancient_sanctuary = Location("Sanctuaire Ancien",":orange_square:","Vous pouvez voler une carte équipement au joueur de votre choix.")

location_list = [hermit_lair, otherworld_door, monastery, graveyard, haunted_forest, ancient_sanctuary]

location_dictionary = {
"Antre de l'Ermite": hermit_lair,
"Porte de l'Outremonde": otherworld_door,
"Monastère": monastery,
"Cimetière": graveyard,
"Forêt Hantée": haunted_forest,
"Sanctuaire Ancien": ancient_sanctuary
}
