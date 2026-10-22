# Imports
import numpy as np 
import itertools
import argparse
import time
import random as RD
from matplotlib import pyplot as plt
from scipy.integrate import odeint
from scipy import zeros_like
from itertools import count
from scipy import integrate
import os
from collections import OrderedDict


# Global variables

# Classes

'''
This class generates and then solves the odes for the binary case of n actions. In this class the
actions are not considered to be mutually exclusive. Consensus does not seem to be reachable. Not
sure if this is a facet of the model or of the mathematics.
'''

class odeGeneratorBinary():

	def __init__(self,number_of_actions = 2):

		self.number_of_actions = number_of_actions

		# Generate all possible belief state vectors
		self.belief_states = [0.0,1.0]
		self.belief_vectors = list(itertools.product(self.belief_states,repeat = self.number_of_actions))

		print self.belief_vectors

	def transition_products(self,belief_state_vector_1,belief_state_vector_2):

		joint_possible_products = [self.possible_product_states(belief_state_vector_1[x],belief_state_vector_2[x]) for x in range(len(belief_state_vector_1))]

		cartesian_product = [x for x in itertools.product(*joint_possible_products)]

		return cartesian_product

	def possible_product_states(self,belief_state_1,belief_state_2):

		if (belief_state_1 == 0.0 and belief_state_2 == 0.0):
			possible_product_states = [0.0, 1.0]
		elif (belief_state_1 == 1.0 and belief_state_2 == 1.0):
			possible_product_states = [0.0,1.0]
		elif (belief_state_1 == 0.0 and belief_state_2 == 1.0):
			possible_product_states = [1.0]
		elif (belief_state_1 == 1.0 and belief_state_2 == 0.0):
			possible_product_states = [0.0]

		return possible_product_states

	
	def generate_transition_data_structure(self):

		transition_data_structure =  {self.belief_vectors.index(x) : {self.belief_vectors.index(y): {self.belief_vectors.index(z): np.power(0.5,np.abs(np.subtract(x,z)).tolist().count(1)) for z in self.transition_products(x,y)} for y in self.belief_vectors if x != y} for x in self.belief_vectors}


	
		return transition_data_structure






# Script

if __name__ == "__main__":

	argument_parse = argparse.ArgumentParser()

	argument_parse.add_argument('-m','--mode',help = " 1 = single run, 2 = multiple runs for average")
	argument_parse.add_argument('-l','--language',help = "language size")
	argument_parse.add_argument('-it','--iterations', help = "number of iterations")


	args = vars(argument_parse.parse_args())

	language_size = int(args['language'])
	mode = int(args['mode'])
	iterations = int(args['iterations'])

	running_time_list = []

	ode_generator = odeGeneratorBinary(language_size)
	
	start_time = time.time()

	global data_structure

	data_structure = ode_generator.generate_transition_data_structure()

	time_taken = time.time()-start_time

	print 'Time taken to generate odes: ', time_taken

	number_states = np.power(2,language_size)

	consensus_counts = np.zeros(number_states)


	
	def f(X,t):

		dotX = zeros_like(X)


		for belief_vector_index in range(number_states-1):
	

			reductive_indices = [x for x in itertools.chain.from_iterable(data_structure[belief_vector_index].values())]
 			multiplicative_coefficients = [x for x in itertools.chain.from_iterable([x.values() for x in data_structure[belief_vector_index].values()])]
			dotX[belief_vector_index] -= X[belief_vector_index]*(sum([X[reductive_indices[x]]*multiplicative_coefficients[x] for x in range(len(reductive_indices))]))


			additive_indices = []
			multiplicative_coefficients = []
			for x,y in data_structure.iteritems():
				for key in y.keys():
					if key == belief_vector_index:

						additive_indices.append([[x,k] for k in y[key].keys()])
						multiplicative_coefficients.append(y[key].values())	

			multiplicative_coefficients = [item for sublist in multiplicative_coefficients for item in sublist]
			additive_indices = [item for sublist in additive_indices for item in sublist]


			#additive_indices_unique = [set(x) for x in additive_indices]
			#additive_indices_unique_list = [list(item) for item in set(frozenset(item) for item in additive_indices)]
			#multiplicative_coefficients = [multiplicative_coefficients[additive_indices_unique.index(set(x))] for x in additive_indices_unique_list]
			#dotX[belief_vector_index] += sum([X[additive_indices_unique_list[x][0]]*X[additive_indices_unique_list[x][1]]*multiplicative_coefficients[x] for x in range(len(additive_indices_unique_list))])

			dotX[belief_vector_index] += sum([X[additive_indices[x][0]]*X[additive_indices[x][1]]*multiplicative_coefficients[x] for x in range(len(additive_indices))])

		dotX[-1] = sum(dotX)
	
		return dotX


	if mode == 1:


		Xo = np.random.normal(1./number_states,0.005,number_states)

		Xo = [float(i)/sum(Xo) for i in Xo]

		t =  np.linspace(0, 100., 1000) 

		start_time = time.time()

		soln = odeint(f, Xo, t)

		time_taken = time.time()-start_time

		print 'Time taken to solve odes: ' + str(time_taken)

		plt.figure()

		for x in range(np.power(2,language_size)):
			plt.plot(t,soln[:,x])

		for k in range(len(soln[:,0])):
			proportion_array = [np.round(x,3) for x in soln[k,:]]
			try:
				consensus_check = proportion_array.index(1)
				consensus_time = t[k]
				consensus_index = k
				break
			except:
				pass

		final_proportions = [soln[-1,x] for x in range(number_states)]

		consensus_index = final_proportions.index(max(final_proportions))

		consensus_counts[consensus_index] += 1

		plt.title('Average conensus reached on belief vector:'+ str(ode_generator.belief_vectors[consensus_index]))
		plt.xlabel('Time (s)')
		plt.ylabel('Proportion of agents')
		plt.show()

		print 'Average consensus reached on belief vector:', ode_generator.belief_vectors[consensus_index]

		


	if mode == 2:

		consensus_counts = np.zeros(number_states)
		consensus_times = np.zeros(iterations)

		for iteration in range(iterations):

			Xo = np.random.normal(1./number_states,0.005,number_states)

			Xo = [float(i)/sum(Xo) for i in Xo]

			t =  np.linspace(0, 100., 1000) 

			soln = odeint(f, Xo, t)

			final_proportions = [soln[-1,x] for x in range(number_states)]

			for k in range(len(soln[:,0])):
				proportion_array = [np.round(x,3) for x in soln[k,:]]
				try:
					consensus_check = proportion_array.index(1)
					consensus_time = t[k]
					consensus_index = k
					consensus_times[iteration] = consensus_time		
					break
				except:
					pass



			consensus_index = final_proportions.index(max(final_proportions))

			consensus_counts[consensus_index] += 1

			fraction_complete = float(iteration)/float(iterations)

			print "\nFraction of iterations completed: " + str(fraction_complete)



		non_zero_indices = [np.where(consensus_counts!=0)[0][x] for x in range(len(np.where(consensus_counts!=0)[0]))]
		
		possible_consensus_states = np.arange(number_states)

		base_path = '/home/sal/Documents/Project/Python_Data/ODE/Not_Exclusive/Binary/'

		folders = 0
		for _, dirnames, filenames in os.walk(base_path):
			folders += len(dirnames)

		trial_number = folders+ 1

		trial_directory = '/home/sal/Documents/Project/Python_Data/ODE/Not_Exclusive/Binary/' + 'trial_' + str(trial_number)

		if not os.path.exists(trial_directory):
			os.makedirs(trial_directory)
			print 'Creating directory...'

		average_time_to_consensus = np.round(np.mean(consensus_times),2)

		plt.bar(possible_consensus_states, consensus_counts, align='center', alpha=0.5)	
		plt.xlabel('Belief state')
		plt.ylabel('Times consensus reached on this belief state')
		consensus_counts = consensus_counts.tolist()

		plt.title('Average conensus reached on belief vector: '+ str(ode_generator.belief_vectors[consensus_counts.index(max(consensus_counts))]) + '\nAverage time to reach consensus: ' +str(average_time_to_consensus))
		plt.savefig(trial_directory +  '/ode_binary.tiff')

		belief_vectors_file = open(trial_directory + '/belief_vectors.csv','w')
		belief_vectors_file.write('Number of iterations: ' + str(iterations))
		belief_vectors_file.write('Language_size: ' + str(language_size))

		count = 0
		for belief_vector in ode_generator.belief_vectors:
			belief_vectors_file.write('\nBelief vector ' + str(count) + ' ' + str(belief_vector))
			count +=1
		belief_vectors_file.close()

		belief_vectors_non_zero_file = open(trial_directory + '/belief_vectors_non_zero.csv','w')
		belief_vectors_non_zero_file.write('Number of iterations: ' + str(iterations))
		count = 0
		for index in non_zero_indices:
			belief_vectors_non_zero_file.write('\nBelief vector ' + str(count) + ' ' + str(ode_generator.belief_vectors[index]))
			count +=1


		belief_vectors_non_zero_file.close()




