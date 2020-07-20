import random


attack_blocked_file = open('quotes/quotes-attack-blocked.txt','r')
attack_6_plus_file = open('quotes/quotes-attack-6-plus.txt','r')
attack_3_to_5_file = open('quotes/quotes-attack-3-to-5.txt','r')
attack_1_to_2_file = open('quotes/quotes-attack-1-to-2.txt','r')
attack_0_file = open('quotes/quotes-attack-0.txt','r')

attack_blocked_quotes = attack_blocked_file.readlines()
attack_6_plus_quotes = attack_6_plus_file.readlines()
attack_3_to_5_quotes = attack_3_to_5_file.readlines()
attack_1_to_2_quotes = attack_1_to_2_file.readlines()
attack_0_quotes = attack_0_file.readlines()

attack_blocked_file.close()
attack_6_plus_file.close()
attack_3_to_5_file.close()
attack_1_to_2_file.close()
attack_0_file.close()

def attack_blocked():
	return (random.sample(attack_blocked_quotes,1))[0]

def attack_6_plus():
	return (random.sample(attack_6_plus_quotes,1))[0]

def attack_3_to_5():
	return (random.sample(attack_3_to_5_quotes,1))[0]

def attack_1_to_2():
	return (random.sample(attack_1_to_2_quotes,1))[0]

def attack_0():
	return (random.sample(attack_0_quotes,1))[0]
