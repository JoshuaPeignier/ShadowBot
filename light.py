class LightCard:
	name = ''
	article = ''
	sort = ''

	## Initialisation of the player
	def __init__(self,name,article,sort):
		self.name = name
		self.article = article
		self.sort = sort

	def fullName(self):
		space = ''
		if self.article != 'l\'':
			space = ' '
		return self.article+space+'**'+self.name+'** *('+self.sort+'*)'

holy_water_card = LightCard('Eau bénite','l\'','effet immédiat')
mirror_card = LightCard('Miroir divin','le','effet immédiat')
divine_lightning_card = LightCard('Eclair divin','l\'','effet immédiat')
chocolate_bar_card = LightCard('Barre de chocolat','la','effet immédiat')
lay_on_hands_card = LightCard('Imposition des mains','l\'','effet immédiat')
first_aid_card = LightCard('Trousse de soins','la','effet immédiat')
benediction_card = LightCard('Bénédiction','la','effet immédiat')
guardian_angel_card = LightCard('Ange gardien','l\'','effet immédiat')
new_turn_card = LightCard('Savoir ancestral','le','effet immédiat')
hookshot_card = LightCard('Grappin','le','effet immédiat')
fraud_repression_card = LightCard('Répression des fraudes','la','effet immédiat')

amulet_card = LightCard('Amulette','l\'','équipement')
pin_card = LightCard('Broche','la','équipement')
ring_card = LightCard('Bague','la','équipement')
compass_card = LightCard('Boussole','la','équipement')
spear_card = LightCard('Lance','la','équipement')
robe_card = LightCard('Toge','la','équipement')
cross_card = LightCard('Crucifix','le','équipement')

light_pool = [holy_water_card,holy_water_card,mirror_card,divine_lightning_card,chocolate_bar_card,lay_on_hands_card,first_aid_card,benediction_card,guardian_angel_card,new_turn_card,hookshot_card,spear_card,robe_card,compass_card,ring_card,amulet_card,cross_card,pin_card]
