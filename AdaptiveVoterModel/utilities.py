# Imports

import numpy as np
from itertools import count


## Find unique states from a set of states
def unique_states(states):

	unique_states = []
	for state in states:
		if state not in unique_states:
			unique_states.append(state)

	return unique_states


## Inconsistency measure for exclusive proposition case


def exclusive_inconsitency_measure(listener,speaker,number_propositions)

	### Modelling assumption: 

	### If both agents are certain of 1 proposition then they are inconsistent (==1) if their beliefs are different 
	### and consistent otherwise (==0)
	
	### Otherwise we take the proportion of propositions on which they disagree as in the non-exclusive case but this time
	### we consider the vagues cases i.e. 1/2   +   0 --> would be considered inconsistent 
	listener_set = listener['state']
	speaker_set = speaker['state']

	if len(listener_set) && len(speaker_set) == 1:
		intersection  = listener_set & speaker_set
		inconsistency = 1 - len(intersection)
	else:

		inconsistency = float(len((listener_set | speaker_set)) - len(listener_set & speaker_set)) / float(number_propositions)


## Inconsistency measure for non-exclusive case
def inconsistency_measure(listener,speaker,number_of_actions):

	listener_belief_vector = listener['state']
	speaker_belief_vector = speaker['state']
	
	### Modelling assumption: 

	### The inconsistency is the proportion of propositions on which they disagree

	combination = float(abs(np.subtract(listener_belief_vector,speaker_belief_vector)).tolist().count(1))

	inconsistency = combination/float(number_of_actions)

	return inconsistency


