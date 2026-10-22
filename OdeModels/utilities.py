# Imports

import numpy as np
from itertools import count

def unique_states(states):

	unique_states = []
	for state in states:
		if state not in unique_states:
			unique_states.append(state)

	return unique_states


def inconsistency_measure(listener,speaker,number_of_actions):

	listener_belief_vector = listener['state']
	speaker_belief_vector = speaker['state']
	
	combination = float(abs(np.subtract(listener_belief_vector,speaker_belief_vector)).tolist().count(1))

	inconsistency = combination/float(number_of_actions)

	return inconsistency
