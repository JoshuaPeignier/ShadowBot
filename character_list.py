import characters

# Hunters
gabrielle = characters.Character("Gabrielle",12,"Hunter",":blue_circle:","Tous les personnages Shadows sont morts.","*Aura de Dévotion (Passif)* | Les attaques infligent une Blessure de moins aux Hunters révélés situés sur le même secteur que vous.",False,True)
gregor = characters.Character("Gregor",14,"Hunter",":blue_circle:","Tous les personnages Shadows sont morts.","*Bouclier Fantôme (Activable, Utilisation unique)* | Vous ne subissez aucune Blessure jusqu'à votre prochain tour. Ce pouvoir ne peut être activé qu'en fin de tour.",True,True)
georges = characters.Character("Georges",14,"Hunter",":blue_circle:","Tous les personnages Shadows sont morts.","*Démolition (Activable, Utilisation unique)* | Au début de votre tour, choisissez un joueur et infligez-lui autant de Blessures que le résultat d'un dé 4.",True,True)
franklin = characters.Character("Franklin",12,"Hunter",":blue_circle:","Tous les personnages Shadows sont morts.","*Foudre (Activable, Utilisation unique)* | Au début de votre tour, choisissez un joueur et infligez-lui autant de Blessures que le résultat d'un dé 6.",True,True)
fuka = characters.Character("Fu-Ka",12,"Hunter",":blue_circle:","Tous les personnages Shadows sont morts.","*Soins particuliers (Activable, Utilisation unique)* | Au début de votre tour, choisissez un joueur et placez directement sa barre de vie à 7 Blessures.",True,True)
emi = characters.Character("Emi",12,"Hunter",":blue_circle:","Tous les personnages Shadows sont morts.","*Téléportation (Conditionné)* | Au début de votre tour, vous pouvez choisir de vous déplacer en lançant les dés ou bien vous déplacer directement sur un des lieux adjacents à la vôtre.",False,True)
ellen = characters.Character("Ellen",10,"Hunter",":blue_circle:","Tous les personnages Shadows sont morts.","*Exorcisme (Activable, Utilisation unique)* | Au début de votre tour, choisissez un joueur ; son pouvoir disparaît jusqu'à la fin de la partie.",True,True)
erik = characters.Character("Erik",10,"Hunter",":blue_circle:","Tous les personnages Shadows sont morts.","*Tranquilité (Activable, Utilisation unique)* | Au début de votre tour et au début de votre prochain tour, vous pouvez choisir entre vous soigner 3 Blessures, ou soigner 2 Blessures à au plus 3 Personnages de votre choix sur votre secteur.",True,True)
link = characters.Character("Link",14,"Hunter",":blue_circle:","Tous les personnages Shadows sont morts.","*Blocage (Passif)* | Lorsque vous subissez une attaque, lancez les deux dés et calculez le résultat comme pour un jet d'attaque. Si le résultat de votre jet est strictement supérieur au résultat du jet de l'attaque adverse, vous ne subissez aucune Blessure.",False,True)
marth = characters.Character("Marth",12,"Hunter",":blue_circle:","Tous les personnages Shadows sont morts.","*Perforation (Passif)* | Lorsque vous attaquez un joueur situé sur un lieu adjacent au vôtre et ne faites pas 0, vous lui infligez une Blessure supplémentaire.",False,True)

# Shadows
werewolf = characters.Character("Loup-Garou",14,"Shadow",":red_circle:","Tous les personnages Hunters sont morts.","*Contre-Attaque (Conditionné) * | Après avoir subi l'attaque d'un joueur, vous pouvez contre-attaquer immédiatement (sans vos équipements).",False,True)
lich = characters.Character("Liche",14,"Shadow",":red_circle:","Tous les personnages Hunters sont morts.","*Nécromancie (Activable, Utilisation unique)* | A la fin de votre tour, rejouez autant de fois qu'il y a de personnages morts.",True,True)
vampire = characters.Character("Vampire",13,"Shadow",":red_circle:","Tous les personnages Hunters sont morts.","*Morsure (Passif)* | Si vous attaquez un joueur et lui infligez des Blessures, soignez une de vos Blessures.",False,True)
valkyrie = characters.Character("Valkyrie",13,"Shadow",":red_circle:","Tous les personnages Hunters sont morts.","*Chant de Guerre (Passif)* | Lorsque vous attaquez, lancez uniquement le dé 4 pour déterminer le montant de dégâts infligés. Par rapport à un jet normal, cela vous empêche de faire 0 et augmente vos chances de faire 3 ou 4.",False,True)
varimathras = characters.Character("Varimathras",13,"Shadow",":red_circle:","Tous les personnages Hunters sont morts.","*Sommeil (Activable, Utilisation unique)* | A la fin de votre tour, choisissez un joueur. Celui-ci passe ses deux prochains tours ; l'effet s'interrompt si la cible subit des Blessures.",True,True)
metamorph = characters.Character("Métamorphe",11,"Shadow",":red_circle:","Tous les personnages Hunters sont morts.","*Imitation* | Lorsqu'on vous donne une carte vision, vous pouvez (sans avoir à révéler votre carte de Personnage) choisir de mentir ou de dire la vérité.",False,False)
mummy = characters.Character("Momie",11,"Shadow",":red_circle:","Tous les personnages Hunters sont morts.","*Voile Mortel (Conditionné)* | Au début de votre tour, vous pouvez infliger 3 Blessures à un joueur de votre choix situé sur la Porte de l'Outremonde.",False,True)
mograine = characters.Character("Mograine",11,"Shadow",":red_circle:","Tous les personnages Hunters sont morts.","*Enchaînement (Conditionné)* | Lorsque vous attaquez, vous pouvez choisir deux cibles et faire un seul jet. La deuxième cible désignée subit la moitié des dégâts de l'attaque.",False,True)
ganondorf = characters.Character("Ganondorf",14,"Shadow",":red_circle:","Tous les personnages Hunters sont morts.","*DORIYAH! (Passif)* | Si vous ne faites pas 0 lors d'une attaque, vous infligez une Blessure supplémentaire par Equipement de Ténèbres en votre possession (le total de dégâts bonus obtenus par vos équipements ET votre pouvoir ne peut pas dépasser 3).",False,True)
majora = characters.Character("Majora",11,"Shadow",":red_circle:","Tous les personnages Hunters sont morts.","*Impact lunaire (Activable, Utilisation unique)* | Au début de votre tour, infligez 2 Blessures à tous les joueurs situés sur un autre secteur que le vôtre",True,True)

# Neutral
daniel = characters.Character("Daniel",13,"Neutre",":yellow_circle:","Être le premier à mourir OU être en vie quand tous les personnages Shadows sont morts.","*Désespoir* | dès qu'un autre personnage meurt, votre identité est automatiquement révélée.",False,False)
catherine = characters.Character("Catherine",11,"Neutre",":yellow_circle:","Être la première à mourir OU être l'un des deux seuls personnages en vie à la fin de la partie.","*Stigmates (Passif)* | Au début de votre tour, soignez une de vos Blessures.",False,True)
allie = characters.Character("Allie",8,"Neutre",":yellow_circle:","Être en vie à la fin de la partie.","*Régénération (Activable, Utilisation unique)* | A n'importe quel moment, vous pouvez soigner toutes vos Blessures.",True,True)
agnes = characters.Character("Agnès",8,"Neutre",":yellow_circle:","Le joueur qui vous précède dans l'ordre du tour gagne.","*Opportunisme (Activable, Utilisation unique)* | A n'importe quel moment, vous pouvez changer votre condition de victoire comme suit : vous gagnez désormais si le joueur qui vous suit dans l'ordre du tour gagne.",True,True)
neo = characters.Character("Neo",11,"Neutre",":yellow_circle:","Le joueur qui vous précède dans l'ordre du tour est en vie à la fin de la partie OU vous êtes en vie quand le joueur qui l'a tué est mort. Si vous tuez vous même le joueur qui vous précède ou s'il se suicide, vous perdez et mourez instantanément.","*Adrénaline (Passif)* | Dès que le joueur qui vous précède meurt, votre identité est automatiquement révélée. Toutes les Blessures que vous inflige le joueur qui l'a tué sont réduites de 1.",False,False)
bob = characters.Character("Bob",11,"Neutre",":yellow_circle:","Posséder 4 cartes équipement ou plus.","*Braquage (Conditionné)* | Si vous piochez une carte Lumière ou Ténèbres à effet immédiat, vous pouvez piocher une autre carte du même type (une fois par tour).",False,True)
bryan = characters.Character("Bryan",11,"Neutre",":yellow_circle:","Être en vie quand le joueur qui vous précède et celui qui vous suit dans l'ordre du tour sont morts.","*OH MY GOD!* | Si vous tuez un autre joueur que ceux-ci, votre identité est automatiquement révélée.",False,False)

char_dictionary = {
"Gabrielle": gabrielle,
"Gregor": gregor,
"Georges": georges,
"Franklin": franklin,
"Fu-Ka": fuka,
"Emi": emi,
"Ellen": ellen,
"Erik": erik,
"Link": link,
"Marth": marth,
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
"Daniel": daniel,
"Catherine": catherine,
"Allie": allie,
"Agnès": agnes,
"Neo": neo,
"Bob": bob,
"Bryan": bryan
}

hunter_list=[gabrielle,gregor,georges,franklin,fuka,emi,ellen,erik,link,marth]

shadow_list=[werewolf,lich,vampire,valkyrie,varimathras,metamorph,mummy,mograine,ganondorf,majora]

neutral_list=[daniel,catherine,allie,agnes,neo,bob,bryan]
#neutral_list=[daniel]
