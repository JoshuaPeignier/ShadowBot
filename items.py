class Item:
	name = ''
	article = ''
	description = ''
	emoji = ''

	## Initialisation of the player
	def __init__(self,name,article,emoji,description):
		self.name = name
		self.article = article
		self.emoji = emoji
		self.description = description

	def getInfo(self):
		return '**'+self.name+'** '+str(self.emoji)+' : '+self.description

	def getEmoji(self):
		return self.emoji

	def getName(self):
		return self.name

	def getNameEmoji(self):
		return self.name+' '+str(self.emoji)

	def getArticleNameEmoji(self):
		space = ''
		if self.article != 'l\'':
			space = ' '
		return self.article+space+'**'+self.name+'** '+str(self.emoji)


bow = Item('Arc','l\'','\U0001F3F9','Vous pouvez attaquer les joueurs situés sur les autres secteurs, mais plus ceux situés sur votre secteur.')
amulet = Item('Amulette','l\'','\U0001F4FF','Vous ne subissez aucune Blessure des cartes Ténèbres suivantes : *Chauve-souris vampire*, *Araignée sanguinaire*, *Dynamite*.')
ring = Item('Bague','la','\U0001F48D','Lorsque vous recevez cet objet, soignez 1 Blessure. Chaque fois que vous arrivez sur le Sanctuaire Ancien, soignez 1 Blessure.')
compass = Item('Boussole','la','\U0001F9ED','Au début de votre tour, les dés sont lancés 2 fois, et vous choisissez le résultat que vous gardez.')
pin = Item('Broche','la','\U0001F4CD','Le pouvoir de la Forêt Hantée ne peut pas vous infliger de dégâts.')
cross = Item('Crucifix','le','\u271D','Lorsque vous tuez un joueur, récupérez tous ses équipements.')
zweihander = Item('Espadon','l\'','\u2694','Vos attaques infligent 1 Blessure supplémentaire si vous ne faites pas 0.')
axe = Item('Hache','la','\U0001FA93','Vos attaques infligent 1 Blessure supplémentaire si vous ne faites pas 0.')
aids = Item('Idole','l\'','\U0001F5FF','Lorsque vous recevez cet objet, subissez 1 Blessure. Au début de votre tour, lancez un dé 6 :\n'
		+ '1 à 3 : Subissez 1 Blessure.\n'
		+ '4 ou 5 : Donnez cet objet à un autre joueur.\n'
		+ '6 : Défaussez cet objet.\n')
katana = Item('Katana','le','\U0001F5E1','Vous êtes obligé d\'attaquer si un joueur est à votre portée. Vous attaquez en ne lançant qu\'un dé 4, dont le résultat donne les dégâts infligés.')
spear = Item('Lance','la','\U0001F9AF','Si vous êtes Hunter :blue_circle: ou Métamorphe :red_circle: et êtes révélé, vos attaques infligent 2 Blessures supplémentaires si vous ne faites pas 0.')
mace = Item('Masse','la','\U0001F528','Vos attaques infligent 1 Blessure supplémentaire si vous ne faites pas 0.')
gunmachine = Item('Mitrailleuse','la','\U0001F52B','Vos attaques touchent tous les joueurs à votre portée.')
robe = Item('Toge','la','\U0001F9BA','Vos attaques infligent 1 Blessure en moins. Toutes les Blessures que vous subissez sont réduites de 1.')

item_dictionary = {
'Arc' : bow,
'Amulette' : amulet,
'Bague' : ring,
'Boussole' : compass,
'Broche' : pin,
'Crucifix' : cross,
'Espadon' : zweihander,
'Hache' : axe,
'Idole' : aids,
'Katana' : katana,
'Lance' : spear,
'Masse' : mace,
'Mitrailleuse' : gunmachine,
'Toge' : robe
}

emoji_to_item_dictionary = {
'\U0001F3F9' : bow,
'\U0001F4FF' : amulet,
'\U0001F48D' : ring,
'\U0001F9ED' : compass,
'\U0001F4CD' : pin,
'\u271D' : cross,
'\u2694' : zweihander,
'\U0001FA93' : axe,
'\U0001F5FF' : aids,
'\U0001F5E1' : katana,
'\U0001F9AF' : spear,
'\U0001F528' : mace,
'\U0001F52B' : gunmachine,
'\U0001F9BA' : robe
}

