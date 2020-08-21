import characters

# Hunters
gabrielle = characters.Character("Gabrielle",12,"Hunter",":blue_circle:","Tous les personnages Shadows sont morts.","*Aura de Dévotion (Passif)* | Les attaques infligent une Blessure de moins aux Hunters révélés situés sur le même secteur que vous.",False,True)
gregor = characters.Character("Gregor",14,"Hunter",":blue_circle:","Tous les personnages Shadows sont morts.","*Bouclier Fantôme (Activable, Utilisation unique)* | Vous ne subissez aucune Blessure jusqu'à votre prochain tour. Ce pouvoir ne peut être activé qu'en fin de tour.",True,True)
georges = characters.Character("Georges",14,"Hunter",":blue_circle:","Tous les personnages Shadows sont morts.","*Démolition (Activable, Utilisation unique)* | Au début de votre tour, choisissez un joueur et infligez-lui autant de Blessures que le résultat d'un dé 4.",True,True)
franklin = characters.Character("Franklin",12,"Hunter",":blue_circle:","Tous les personnages Shadows sont morts.","*Foudre (Activable, Utilisation unique)* | Au début de votre tour, choisissez un joueur et infligez-lui autant de Blessures que le résultat d'un dé 6.",True,True)
fuka = characters.Character("Fu-Ka",12,"Hunter",":blue_circle:","Tous les personnages Shadows sont morts.","*Soins particuliers (Activable, Utilisation unique)* | Au début de votre tour, choisissez un joueur et placez directement sa barre de vie à 7 Blessures.",True,True)
emi = characters.Character("Emi",12,"Hunter",":blue_circle:","Tous les personnages Shadows sont morts.","*Téléportation (Conditionné)* | Au début de votre tour, vous pouvez choisir de vous déplacer en lançant les dés ou bien vous déplacer directement sur un des lieux adjacents à la vôtre.",False,True)
ellen = characters.Character("Ellen",10,"Hunter",":blue_circle:","Tous les personnages Shadows sont morts.","*Exorcisme (Activable, Utilisation unique)* | Au début de votre tour, choisissez un joueur ; son pouvoir disparaît jusqu'à la fin de la partie. De plus, si c'est un Shadow autre que Métamorphe, vous vous soignez 3 Blessures, et il est forcé de révéler son identité si elle ne l\'était pas déjà.",True,True)
erik = characters.Character("Erik",10,"Hunter",":blue_circle:","Tous les personnages Shadows sont morts.","*Tranquilité (Activable, Utilisation unique)* | Au début de votre tour et au début de votre prochain tour, vous pouvez choisir entre vous soigner 3 Blessures, ou soigner 2 Blessures à au plus 3 Personnages de votre choix sur votre secteur.",True,True)
lothaire = characters.Character("Lothaire",14,"Hunter",":blue_circle:","Tous les personnages Shadows sont morts.","*Blocage (Passif)* | Lorsque vous subissez une attaque, lancez les deux dés et calculez le résultat comme pour un jet d'attaque. Si votre jet fait au moins 2 de plus que le jet adverse, vous ne subissez aucune Blessure.",False,True)
marth = characters.Character("Marth",12,"Hunter",":blue_circle:","Tous les personnages Shadows sont morts.","*Perforation (Passif)* | Lorsque vous attaquez un joueur situé sur un lieu adjacent au vôtre et ne faites pas 0, vous lui infligez une Blessure supplémentaire.",False,True)
link = characters.Character("Link",12,"Hunter",":blue_circle:","Tous les personnages Shadows sont morts.","*Bombe glitchée (Conditionné)* | Au début de votre tour, vous pouvez subir une Blessure pour lancer deux fois les dés pour votre déplacement, et choisir le résultat.",False,True)

# Shadows
werewolf = characters.Character("Loup-Garou",14,"Shadow",":red_circle:","Tous les personnages Hunters sont morts.","*Contre-Attaque (Conditionné) * | Après avoir subi l'attaque d'un joueur, vous pouvez contre-attaquer immédiatement (sans vos équipements).",False,True)
lich = characters.Character("Liche",14,"Shadow",":red_circle:","Tous les personnages Hunters sont morts.","*Nécromancie (Activable, Utilisation unique)* | A la fin de votre tour, rejouez autant de fois qu'il y a de personnages morts.",True,True)
vampire = characters.Character("Vampire",13,"Shadow",":red_circle:","Tous les personnages Hunters sont morts.","*Morsure (Passif)* | Si vous attaquez un joueur et lui infligez des Blessures, soignez une de vos Blessures.",False,True)
valkyrie = characters.Character("Valkyrie",13,"Shadow",":red_circle:","Tous les personnages Hunters sont morts.","*Chant de Guerre (Passif)* | Lorsque vous attaquez, lancez uniquement le dé 4 pour déterminer le montant de dégâts infligés. Par rapport à un jet normal, cela vous empêche de faire 0 et augmente vos chances de faire 3 ou 4.",False,True)
varimathras = characters.Character("Varimathras",13,"Shadow",":red_circle:","Tous les personnages Hunters sont morts.","*Sommeil (Activable, Utilisation unique)* | A la fin de votre tour, choisissez un joueur. Celui-ci passe s'endort ses deux prochains tours. S'il subit au moins 2 Blessures en une fois, l'effet s'interrompt. Si le joueur passe son deuxième tour et que vous êtes vivant, il subit 4 Blessures.",True,True)
metamorph = characters.Character("Métamorphe",11,"Shadow",":red_circle:","Tous les personnages Hunters sont morts.","*Imitation* | Lorsqu'on vous donne une carte vision, vous pouvez (sans avoir à révéler votre carte de Personnage) choisir de mentir ou de dire la vérité.",False,False)
mummy = characters.Character("Momie",11,"Shadow",":red_circle:","Tous les personnages Hunters sont morts.","*Voile Mortel (Conditionné)* | Au début de votre tour, vous pouvez infliger 3 Blessures à un joueur de votre choix situé sur la Porte de l'Outremonde.",False,True)
mograine = characters.Character("Mograine",14,"Shadow",":red_circle:","Tous les personnages Hunters sont morts.","*Enchaînement (Conditionné)* | Lorsque vous attaquez, vous pouvez choisir deux cibles et faire un seul jet. La deuxième cible désignée subit la moitié des dégâts de l'attaque.",False,True)
ganondorf = characters.Character("Ganondorf",14,"Shadow",":red_circle:","Tous les personnages Hunters sont morts.","*DORIYAH! (Passif)* | Si vous ne faites pas 0 lors d'une attaque, vous infligez une Blessure supplémentaire par Equipement de Ténèbres en votre possession (le total de dégâts bonus obtenus par vos équipements ET votre pouvoir ne peut pas dépasser 3).",False,True)
majora = characters.Character("Majora",11,"Shadow",":red_circle:","Tous les personnages Hunters sont morts.","*Impact lunaire (Activable, Utilisation unique)* | Au début de votre tour, infligez 2 Blessures à tous les joueurs situés sur un autre secteur que le vôtre",True,True)
charles = characters.Character("Charles",13,"Shadow",":red_circle:","Tous les personnages Hunters sont morts.","*Rage (Passif)* | Si vous ne faites pas 0 lors d'une attaque, vous infligez 1/2/3 Blessures supplémentaires si vous avez subi au moins 5/9/12 Blessures.",False,True)

# Neutral
daniel = characters.Character("Daniel",13,"Neutre",":yellow_circle:","Être le premier à mourir OU être en vie quand tous les personnages Hunters ou Shadows (le camp opposé au premier mort) sont morts.","*Désespoir* | Dès qu'un autre personnage meurt, votre identité est automatiquement révélée. Si le premier mort est un Hunter, vous devez tuer les Shadows, et inversement. Si c'est un Neutre, ou si un Shadow et un Hunter meurent en premier en même temps, vous choisissez votre camp.",False,False)
catherine = characters.Character("Catherine",11,"Neutre",":yellow_circle:","Être la première à mourir OU être l'un des deux seuls personnages en vie à la fin de la partie.","*Stigmates (Passif)* | Au début de votre tour, soignez une de vos Blessures.",False,True)
allie = characters.Character("Allie",8,"Neutre",":yellow_circle:","Être en vie à la fin de la partie.","*Régénération (Activable, Utilisation unique)* | A n'importe quel moment, vous pouvez soigner toutes vos Blessures.",True,True)
agnes = characters.Character("Agnès",8,"Neutre",":yellow_circle:","Le joueur qui vous précède dans l'ordre du tour gagne.","*Opportunisme (Activable, Utilisation unique)* | Au début de votre tour, vous pouvez changer votre condition de victoire comme suit : vous gagnez désormais si le joueur qui vous suit dans l'ordre du tour gagne.",True,True)
angus = characters.Character("Angus",8,"Neutre",":yellow_circle:","Le joueur qui vous précède dans l'ordre du tour gagne.","*Opportunisme (Activable, Utilisation unique)* | Au début de votre tour, vous pouvez changer votre condition de victoire comme suit : vous gagnez désormais si le joueur qui vous précède dans l'ordre du tour perd.",True,True)
neo = characters.Character("Neo",11,"Neutre",":yellow_circle:","Le joueur qui vous précède dans l'ordre du tour est en vie à la fin de la partie OU vous êtes en vie quand le joueur qui l'a tué est mort. Si vous tuez vous même le joueur qui vous précède ou s'il se suicide, vous perdez et mourez instantanément.","*Adrénaline (Passif)* | Dès que le joueur qui vous précède meurt, votre identité est automatiquement révélée. Toutes les Blessures que vous inflige le joueur qui l'a tué sont réduites de 1.",False,False)
bob = characters.Character("Bob",11,"Neutre",":yellow_circle:","Posséder 4 cartes équipement ou plus.","*Braquage (Conditionné)* | Si vous piochez une carte Lumière ou Ténèbres à effet immédiat, vous pouvez piocher une autre carte du même type (une fois par tour).",False,True)
cartouche = characters.Character("Cartouche",11,"Neutre",":yellow_circle:","Posséder 4 cartes équipement ou plus.","*Braquage (Passif)* | Lorsque vous envoyez une carte vision à un joueur possédant des équipements et qu'il a la possibilité de vous en donner, il doit le faire.",False,True)
bryan = characters.Character("Bryan",11,"Neutre",":yellow_circle:","Être en vie quand le joueur qui vous précède et celui qui vous suit dans l'ordre du tour sont morts.","*OH MY GOD!* | Si vous tuez un autre joueur que ceux-ci, votre identité est automatiquement révélée.",False,False)
despair = characters.Character("Despair",13,"Neutre",":yellow_circle:","Être le seul personnage en vie.","*Apocalypse (Passif)* | Lorsque vous attaquez, tous les joueurs encore en vie (excepté vous) subissent les dégâts de votre attaque. De plus, tant que vous êtes en vie et révélé, les Hunters et les Shadows ne peuvent pas gagner.",False,False)

char_dictionary = {
"Gabrielle": gabrielle,
"Gregor": gregor,
"Georges": georges,
"Franklin": franklin,
"Fu-Ka": fuka,
"Emi": emi,
"Ellen": ellen,
"Erik": erik,
"Lothaire": lothaire,
"Marth": marth,
"Link": link,
"Loup-Garou": werewolf,
"Liche": lich,
"Vampire": vampire,
"Valkyrie": valkyrie,
"Varimathras": varimathras,
"Métamorphe": metamorph,
"Momie": mummy,
"Mograine": mograine,
"Ganondorf": ganondorf,
"Majora": majora,
"Charles": charles,
"Daniel": daniel,
"Catherine": catherine,
"Allie": allie,
"Agnès": agnes,
"Angus": angus,
"Neo": neo,
"Bob": bob,
"Cartouche": cartouche,
"Bryan": bryan,
"Despair": despair
}

hunter_list=[gabrielle,gregor,georges,franklin,fuka,emi,ellen,erik,lothaire,marth,link]
#hunter_list=[link,link]

shadow_list=[werewolf,lich,vampire,valkyrie,varimathras,metamorph,mummy,mograine,ganondorf,majora,charles]
#shadow_list=[ganondorf,ganondorf]

neutral_list=[daniel,catherine,allie,agnes,neo,bob,bryan]
#neutral_list=[cartouche,cartouche]

def update_version(nb):
	global gabrielle
	global gregor
	global georges
	global franklin
	global fuka
	global emi
	global ellen
	global erik
	global lothaire
	global marth
	global link
	global werewolf
	global lich
	global vampire
	global valkyrie
	global varimathras
	global metamorph
	global mummy
	global mograine
	global ganondorf
	global majora
	global charles
	global daniel
	global catherine
	global allie
	global agnes
	global neo
	global bob
	global bryan
	global hunter_list
	global shadow_list
	global neutral_list

	if nb == 0:

		ellen.abilityText = "*Exorcisme (Activable, Utilisation unique)* | Au début de votre tour, choisissez un joueur ; son pouvoir disparaît jusqu'à la fin de la partie."
		emi.totalHealth = 10

		vampire.abilityText = "*Morsure (Passif)* | Si vous attaquez un joueur et lui infligez des Blessures, soignez 2 de vos Blessures."

		daniel.wincon = "Être le premier à mourir OU être en vie quand tous les personnages Shadows sont morts."
		daniel.abilityText = "*Désespoir* | Dès qu'un autre personnage meurt, votre identité est automatiquement révélée."

		bob.wincon = "Posséder 5 cartes équipement ou plus."
		bob.abilityText = "*Braquage (Conditionné)* | Si vous tuez un personnage, vous récupérez tous ses équipements."
		bob.totalHealth = 10

		allie.wincon = "Être en vie à la fin de la partie."
		allie.abilityText = "*Régénération (Activable, Utilisation unique)* | A n'importe quel moment, vous pouvez soigner toutes vos Blessures."
		allie.uniqueUse = True
		allie.choice = True

		hunter_list=[gregor,georges,franklin,fuka,emi,ellen]
		shadow_list=[werewolf,lich,vampire,valkyrie,metamorph,mummy]
		neutral_list=[daniel,catherine,allie,agnes,bob]

	elif nb == 1:

		ellen.abilityText = "*Exorcisme (Activable, Utilisation unique)* | Au début de votre tour, choisissez un joueur ; son pouvoir disparaît jusqu'à la fin de la partie. De plus, si c'est un Shadow autre que Métamorphe, vous vous soignez 3 Blessures, et il est forcé de révéler son identité si elle ne l\'était pas déjà."
		emi.totalHealth = 12

		vampire.abilityText = "*Morsure (Passif)* | Si vous attaquez un joueur et lui infligez des Blessures, soignez une de vos Blessures."

		daniel.wincon = "Être le premier à mourir OU être en vie quand tous les personnages Hunters ou Shadows (le camp opposé au premier mort) sont morts."
		daniel.abilityText = "*Désespoir* | Dès qu'un autre personnage meurt, votre identité est automatiquement révélée. Si le premier mort est un Hunter, vous devez tuer les Shadows, et inversement. Si c'est un Neutre, ou si un Shadow et un Hunter meurent en premier en même temps, vous choisissez votre camp."

		bob.wincon = "Posséder 4 cartes équipement ou plus."
		bob.abilityText = "*Braquage (Conditionné)* | Si vous piochez une carte Lumière ou Ténèbres à effet immédiat, vous pouvez piocher une autre carte du même type (une fois par tour)."
		bob.totalHealth = 11

		allie.wincon = "Être en vie et non révélé quand la partie se termine."
		allie.abilityText = "*Campagne électorale* | Lorsqu'un autre joueur vous envoie une carte vision, vous êtes obligé d'y mentir."
		allie.uniqueUse = False
		allie.choice = False

		hunter_list=[gabrielle,gregor,georges,franklin,fuka,emi,ellen,erik,lothaire,marth,link]
		shadow_list=[werewolf,lich,vampire,valkyrie,varimathras,metamorph,mummy,mograine,ganondorf,majora,charles]
		neutral_list=[daniel,catherine,allie,agnes,neo,bob,bryan,despair]
