class VisionCard:
	initiator_text = ''
	receiver_text = ''

	## Initialisation of the player
	def __init__(self,initiator_text,receiver_text):
		self.initiator_text = initiator_text
		self.receiver_text = receiver_text

	def initiatorText(self):
		return self.initiator_text

	def receiverText(self):
		return self.receiver_text

mortifere = VisionCard('Tu peux demander à un joueur s\'il est **Hunter** :blue_circle:. Si c\'est le cas, il devra **subir** **1** Blessure.','Si tu es **Hunter** :blue_circle:, tu dois **subir** **1** Blessure.')
foudroyante = VisionCard('Tu peux demander à un joueur s\'il est **Shadow** :red_circle:. Si c\'est le cas, il devra **subir** **1** Blessure.','Si tu es **Shadow** :red_circle:, tu dois **subir** **1** Blessure.')
purificatrice = VisionCard('Tu peux demander à un joueur s\'il est **Shadow** :red_circle:. Si c\'est le cas, il devra **subir** **2** Blessures.','Si tu es **Shadow** :red_circle:, tu dois **subir** **2** Blessures.')
divine = VisionCard('Tu peux demander à un joueur s\'il est **Hunter** :blue_circle:. Si c\'est le cas, il devra se **soigner** **1** Blessure (ou en **subir** une s\'il n\'en avait pas).','Si tu es **Hunter** :blue_circle:, tu dois te **soigner** **1** Blessure (ou en **subir** une si tu n\'en as pas).')
lugubre = VisionCard('Tu peux demander à un joueur s\'il est **Shadow** :red_circle:. Si c\'est le cas, il devra se **soigner** **1** Blessure (ou en **subir** une s\'il n\'en avait pas).','Si tu es **Shadow** :red_circle:, tu dois te **soigner** **1** Blessure (ou en **subir** une si tu n\'en as pas).')
reconfortante = VisionCard('Tu peux demander à un joueur s\'il est **Neutre** :yellow_circle:. Si c\'est le cas, il devra se **soigner** **1** Blessure (ou en **subir** une s\'il n\'en avait pas).','Si tu es **Neutre** :yellow_circle:, tu dois te **soigner** **1** Blessure (ou en **subir** une si tu n\'en as pas).')
clairvoyante = VisionCard('Tu peux demander à un joueur s\'il a **11 PV ou moins**. Si c\'est le cas, il devra **subir** **1** Blessure.','Si tu as **11 PV ou moins**, tu dois **subir** **1** Blessure.')
destructrice = VisionCard('Tu peux demander à un joueur s\'il a **12 PV ou plus**. Si c\'est le cas, il devra **subir** **2** Blessure.','Si tu as **12 PV ou plus**, tu dois **subir** **2** Blessures.')
furtive = VisionCard('Tu peux demander à un joueur s\'il est **Hunter** :blue_circle: **ou Shadow** :red_circle:. Si c\'est le cas, il devra **subir** **1** Blessure ou te **donner un équipement**.','Si tu es **Hunter** :blue_circle: **ou Shadow** :red_circle:, tu dois **subir** **1** Blessure ou lui **donner un équipement**.')
enivrante = VisionCard('Tu peux demander à un joueur s\'il est **Hunter** :blue_circle: **ou Neutre** :yellow_circle:. Si c\'est le cas, il devra **subir** **1** Blessure ou te **donner un équipement**.','Si tu es **Hunter** :blue_circle: **ou Neutre** :yellow_circle:, tu dois **subir** **1** Blessure ou lui **donner un équipement**.')
cupide = VisionCard('Tu peux demander à un joueur s\'il est **Shadow** :red_circle: **ou Neutre** :yellow_circle:. Si c\'est le cas, il devra **subir** **1** Blessure ou te **donner un équipement**.','Si tu es **Shadow** :red_circle: **ou Neutre** :yellow_circle:, tu dois **subir** **1** Blessure ou lui **donner un équipement**.')
supreme = VisionCard('Tu peux **connaître le personnage** d\'un joueur.','\"Je vais regarder ton rôle.\"')

# In a sudden death game with 4 players (reconfortante is not present because, because it is supposed to be useless with 4 players)
vision_pool_basic = [mortifere,mortifere,foudroyante,purificatrice,divine,lugubre,clairvoyante,destructrice,furtive,furtive,enivrante,enivrante,cupide,cupide]

# In a sudden death game with at least 5 players
vision_pool_sudden_death = vision_pool_basic+[reconfortante]

# In a 4 players game which is NOT a sudden death game
vision_pool_no_neutral = vision_pool_basic+[supreme]

# Classical vision_pool
vision_pool_default = vision_pool_basic+[reconfortante,supreme]
