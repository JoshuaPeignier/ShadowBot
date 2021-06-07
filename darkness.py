class DarknessCard:
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

vampire_bat_card = DarknessCard('Chauve-souris vampire','la','effet immédiat')
spider_card = DarknessCard('Araignée sanguinaire','l\'','effet immédiat')
dynamite_card = DarknessCard('Dynamite','la','effet immédiat')
voodoo_doll_card = DarknessCard('Poupée Vaudou','la','effet immédiat')
devilish_ritual_card = DarknessCard('Rituel diabolique','le','effet immédiat')
whip_card = DarknessCard('Fouet de dominatrice','le','effet immédiat')
succubus_card = DarknessCard('Succube tentatrice','la','effet immédiat')
banana_peel_card = DarknessCard('Peau de banane','la','effet immédiat')

axe_card = DarknessCard('Hache','la','équipement')
zweihander_card = DarknessCard('Espadon','l\'','équipement')
mace_card = DarknessCard('Masse','la','équipement')
katana_card = DarknessCard('Katana','le','équipement')
gunmachine_card = DarknessCard('Mitrailleuse','la','équipement')
bow_card = DarknessCard('Arc','l\'','équipement')
aids_card = DarknessCard('Idole','l\'','équipement')

darkness_pool = [vampire_bat_card,vampire_bat_card,vampire_bat_card,spider_card,dynamite_card,voodoo_doll_card,devilish_ritual_card,banana_peel_card,succubus_card,succubus_card,whip_card,gunmachine_card,bow_card,katana_card,axe_card,zweihander_card,mace_card,aids_card]

#darkness_pool = [zweihander_card,axe_card,mace_card]

def update_version(nb):
	global darkness_pool
	if nb == 0:
		darkness_pool = [vampire_bat_card,vampire_bat_card,vampire_bat_card,spider_card,dynamite_card,voodoo_doll_card,devilish_ritual_card,banana_peel_card,succubus_card,succubus_card,gunmachine_card,bow_card,katana_card,axe_card,zweihander_card,mace_card]
	elif nb == 1:
		darkness_pool = [vampire_bat_card,vampire_bat_card,vampire_bat_card,spider_card,dynamite_card,voodoo_doll_card,devilish_ritual_card,banana_peel_card,succubus_card,succubus_card,whip_card,gunmachine_card,bow_card,katana_card,axe_card,zweihander_card,mace_card,aids_card]

