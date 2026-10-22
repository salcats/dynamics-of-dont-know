# Imports
import numpy as np
import argparse
import itertools
import time
from utilities import unique_states
from matplotlib import pyplot as plt
from scipy.integrate import odeint
from scipy import zeros_like
import random as RD

# Global variables

# Class

'''
This class generates and then solves the odes for the binary case of n actions. In this class the
actions are considered to be mutually exclusive. Conservation law was used in generating and solving
the odes to ensure that the proportion of agents remained = 1. 


INCOMPLETE

This class is incomplete as need to include some sort of stochastic differential equation instead otherwise
the deterministic odes all have 0 rates...

'''

class MutuallyExclusiveOdeGeneratorBinary():

	def __init__(self,language_size):

		self.language_size = language_size
		self.permissible_state_set_size = language_size
		self.permissible_states = [set([x]) for x in range(1,self.language_size+1)]

def f(X,t):

	# Includes conservation law!
	dotX = zeros_like(X)

	for state_1 in range(number_of_states-1):
		for state_2 in range(number_of_states):
			if state_1 != state_2:

				dotX[state_1] += np.power(-1,RD.choice([1,2]))*0.5*X[state_1]*X[state_2]

	dotX[-1] = -sum(dotX)

	return dotX

# Script

if __name__ == "__main__":

	argument_parse = argparse.ArgumentParser()


	argument_parse.add_argument('-l','--language',help = "language size")
	argument_parse.add_argument('-m','--mode',help = "mode of operation : 1 - single run, 2 - multiple runs")

	args = vars(argument_parse.parse_args())

	language_size = int(args['language'])
	mode = int(args['mode'])

	mutually_exclusive_og = MutuallyExclusiveOdeGeneratorBinary(language_size)
	number_of_states = language_size

	if mode == 1:

		Xo = np.random.normal(1./number_of_states,0.05,number_of_states)

		Xo = [float(i)/sum(Xo) for i in Xo]

		Xo = [0.0,0.5,0.5]



		t =  np.linspace(0, 100., 1000)

		start_time = time.time()
		soln = odeint(f, Xo, t)
		time_taken = time.time()-start_time
		print 'Time taken to solve odes: ' + str(time_taken)

		plt.figure()

		for x in range(number_of_states):
			plt.plot(t,soln[:,x])

		plt.show()

		quit()

		final_proportions = [soln[-1,x] for x in range(number_of_states)]

		consensus_index = final_proportions.index(max(final_proportions))

		consensus_belief = mutually_exclusive_og.find_consensus_belief(consensus_index)

		plt.title('Average conensus reached on belief vector:'+ str(consensus_belief))
		plt.xlabel('Time (s)')
		plt.ylabel('Proportion of agents')
		plt.show()

		#print 'Average consensus reached on belief vector:', ode_generator.belief_state_vectors[consensus_index]





	





