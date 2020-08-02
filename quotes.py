import random


attack_blocked_file = open('quotes/quotes-attack-blocked.txt','r')
attack_missed_file = open('quotes/quotes-attack-missed.txt','r')

attacker_6_plus_file = open('quotes/quotes-attacker-6-plus.txt','r')
attacker_4_to_5_file = open('quotes/quotes-attacker-4-to-5.txt','r')
attacker_0_to_3_file = open('quotes/quotes-attacker-0-to-3.txt','r')

defender_11_to_14_file = open('quotes/quotes-defender-11-to-14.txt','r')
defender_8_to_10_file = open('quotes/quotes-defender-8-to-10.txt','r')
defender_5_to_7_file = open('quotes/quotes-defender-5-to-7.txt','r')
defender_0_to_4_file = open('quotes/quotes-defender-0-to-4.txt','r')


attack_blocked_quotes = attack_blocked_file.readlines()
attack_missed_quotes = attack_missed_file.readlines()

attacker_6_plus_quotes = attacker_6_plus_file.readlines()
attacker_4_to_5_quotes = attacker_4_to_5_file.readlines()
attacker_0_to_3_quotes = attacker_0_to_3_file.readlines()

defender_11_to_14_quotes = defender_11_to_14_file.readlines()
defender_8_to_10_quotes = defender_8_to_10_file.readlines()
defender_5_to_7_quotes = defender_5_to_7_file.readlines()
defender_0_to_4_quotes = defender_0_to_4_file.readlines()


attack_blocked_file.close()
attack_missed_file.close()

attacker_6_plus_file.close()
attacker_4_to_5_file.close()
attacker_0_to_3_file.close()

defender_11_to_14_file.close()
defender_8_to_10_file.close()
defender_5_to_7_file.close()
defender_0_to_4_file.close()

def attack_blocked():
	return (random.sample(attack_blocked_quotes,1))[0]

def attack_missed():
	return (random.sample(attack_missed_quotes,1))[0]

def attacker_6_plus():
	return (random.sample(attacker_6_plus_quotes,1))[0]

def attacker_4_to_5():
	return (random.sample(attacker_4_to_5_quotes,1))[0]

def attacker_0_to_3():
	return (random.sample(attacker_0_to_3_quotes,1))[0]

def defender_11_to_14():
	return (random.sample(defender_11_to_14_quotes,1))[0]

def defender_8_to_10():
	return (random.sample(defender_8_to_10_quotes,1))[0]

def defender_5_to_7():
	return (random.sample(defender_5_to_7_quotes,1))[0]

def defender_0_to_4():
	return (random.sample(defender_0_to_4_quotes,1))[0]
