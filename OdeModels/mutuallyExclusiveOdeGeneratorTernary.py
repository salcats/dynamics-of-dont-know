# Imports
import numpy as np
import argparse
import itertools
import time
from utilities import unique_states
from matplotlib import pyplot as plt
from scipy.integrate import odeint
from scipy import zeros_like
import os
# Global variables

# Class


'''
This class generates and then solves the odes for the ternary case of n actions. In this class the
actions are considered to be mutually exclusive. Conservation law was used in generating and solving
the odes to ensure that the proportion of agents remained = 1
'''

class MutuallyExclusiveOdeGeneratorTernary():

	def __init__(self,language_size):

		self.language_size = language_size
		self.permissible_state_set_size = np.power(2,self.language_size) - 1
		self.state_array = np.zeros((self.permissible_state_set_size,self.permissible_state_set_size))
		self.permissible_states = []

	def find_permissible_states(self):

		base_set = set(range(1,self.language_size+1))

		permissible_states = [[set(y) for y in itertools.combinations(base_set,x)] for x in range(1,self.language_size+1)]
		permissible_states = list(itertools.chain.from_iterable(permissible_states))
		self.permissible_states = permissible_states

		
		# Can speed this up by computing upper triangular indices and then using symmetry to fill in the lower triangle
		# Need to check what the command in numpy is though
		empty_set = set([])
		count_set_1 = 0

		start_time = time.time()
		for set_1 in permissible_states:
			count_set_2 = 0
			for set_2 in permissible_states:
				set_intersection = set_1 & set_2
				if set_intersection == empty_set:
					set_union = set_1 | set_2
					consensus_result = permissible_states.index(set_union)					
					self.state_array[count_set_1,count_set_2] = consensus_result
				
				else:
					consensus_result = permissible_states.index(set_intersection)
					self.state_array[count_set_1,count_set_2] = consensus_result
			
				count_set_2 += 1


			count_set_1 += 1


		print self.state_array
		quit()
		return permissible_states

	def find_additive_indices(self,state_index):

		set_of_indices = np.where(self.state_array == state_index)

		set_indices_row = set_of_indices[0]
		set_indices_col = set_of_indices[1]

		pairs_indices = [set([set_indices_row[x],set_indices_col[x]]) for x in range(len(set_indices_col))]
		pairs_indices = [list(subset) for subset in unique_states(pairs_indices)]
		pairs_indices.remove([state_index])
		
		list_additive_indices = pairs_indices

		return list_additive_indices

	def find_reductive_indices(self,state_index):

		list_reductive_indices = np.where(self.state_array[state_index,:] != state_index)[0].tolist()

		return list_reductive_indices


	def ode_generator(self):

		additive_dict = {x: self.find_additive_indices(x) for x in range(self.permissible_state_set_size)}
		
		reductive_dict = {x: self.find_reductive_indices(x) for x in range(self.permissible_state_set_size)}

		return additive_dict, reductive_dict

	def find_consensus_belief(self,consensus_index):

		consensus_belief = np.zeros((1,number_of_states))
		permissible_states_list = list(self.permissible_states[consensus_index])

		for x in range(len(permissible_states_list)):
			prop_variable = permissible_states_list[x]-1
			consensus_belief[0,prop_variable] = 0.5
		if np.sum(consensus_belief) == 0.5:
			consensus_belief = 2*consensus_belief

		index = np.where(consensus_belief==1)[1]
		if np.where(consensus_belief==1)[1] <=self.language_size:
			consensus_belief = np.zeros((1,self.language_size))
			consensus_belief[0,index] = 1

		return consensus_belief

		



def f(X,t):


	# Includes conservation law!
	dotX = zeros_like(X)

	for state in range(number_of_states-1):

		additive_indices = additive_dict[state]

		for additive_index in additive_indices:

			state_1 = additive_index[0]
			state_2 = additive_index[1]

			dotX[state] += X[state_1]*X[state_2]
			
		reductive_indices = reductive_dict[state]

		for reductive_index in reductive_indices:
			dotX[state] -= X[state] * X[reductive_index]


	dotX[-1] = -sum(dotX)
	
	return dotX

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

	number_of_states = np.power(2,language_size) - 1

	mutually_exclusive_og = MutuallyExclusiveOdeGeneratorTernary(language_size)

	start_time = time.time()
	permissible_states = mutually_exclusive_og.find_permissible_states()
	
	global additive_dict, reductive_dict
	additive_dict, reductive_dict = mutually_exclusive_og.ode_generator()

	time_taken = time.time()-start_time

	print 'Time taken to generate odes: ', time_taken


	if mode == 1:


		Xo = np.random.normal(1./number_of_states,0.005,number_of_states)


		Xo = [float(i)/sum(Xo) for i in Xo]

		t =  np.linspace(0, 100., 1000)

		start_time = time.time()
		soln = odeint(f, Xo, t)
		time_taken = time.time()-start_time
		print 'Time taken to solve odes: ' + str(time_taken)

		plt.figure()

		for x in range(number_of_states):
			plt.plot(t,soln[:,x])

		

		final_proportions = [soln[-1,x] for x in range(number_of_states)]

		consensus_index = final_proportions.index(max(final_proportions))

		consensus_belief = mutually_exclusive_og.find_consensus_belief(consensus_index)

		plt.title('Average conensus reached on belief vector:'+ str(consensus_belief))
		plt.xlabel('Time (s)')
		plt.ylabel('Proportion of agents')
		plt.show()

		#print 'Average consensus reached on belief vector:', ode_generator.belief_state_vectors[consensus_index]



	if mode == 2:

		consensus_counts = np.zeros(number_of_states)
		consensus_times = np.zeros(iterations)

		for iteration in range(iterations):

			Xo = np.random.normal(1./number_of_states,0.005,number_of_states)

			Xo = [float(i)/sum(Xo) for i in Xo]

			t =  np.linspace(0, 100., 1000) 

			soln = odeint(f, Xo, t)

			final_proportions = [soln[-1,x] for x in range(number_of_states)]

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



		belief_vectors = [list(mutually_exclusive_og.permissible_states[x]) for x in range(len(mutually_exclusive_og.permissible_states))]

		non_zero_indices = [np.where(consensus_counts!=0)[0][x] for x in range(len(np.where(consensus_counts!=0)[0]))]
		
		possible_consensus_states = np.arange(number_of_states)

		base_path = '/home/sal/Documents/Project/Python_Data/ODE/Exclusive/Ternary/'

		folders = 0
		for _, dirnames, filenames in os.walk(base_path):
			folders += len(dirnames)

		trial_number = folders+ 1

		trial_directory = '/home/sal/Documents/Project/Python_Data/ODE/Exclusive/Ternary/' + 'trial_' + str(trial_number)

		if not os.path.exists(trial_directory):
			os.makedirs(trial_directory)
			print 'Creating directory...'

		average_time_to_consensus = np.round(np.mean(consensus_times),2)


		plt.bar(possible_consensus_states, consensus_counts, align='center', alpha=0.5)	
		plt.xlabel('Belief state')
		plt.ylabel('Times consensus reached on this belief state')
		consensus_counts = consensus_counts.tolist()

		plt.title('Average conensus reached on belief vector: '+ str(belief_vectors[consensus_counts.index(max(consensus_counts))]) + '\nAverage time to reach consensus: ' +str(average_time_to_consensus))
		plt.savefig(trial_directory +  '/ode_ternary.tiff')

		belief_vectors_file = open(trial_directory + '/belief_vectors.csv','w')
		belief_vectors_file.write('Number of iterations: ' + str(iterations))
		belief_vectors_file.write('Language_size: ' + str(language_size))

		count = 0
		for belief_vector in belief_vectors:
			belief_vectors_file.write('\nBelief vector ' + str(count) + ' ' + str(belief_vector))
			count +=1
		belief_vectors_file.close()



		belief_vectors_non_zero_file = open(trial_directory + '/belief_vectors_non_zero.csv','w')
		belief_vectors_non_zero_file.write('Number of iterations: ' + str(iterations))
		count = 0
		for index in non_zero_indices:
			belief_vectors_non_zero_file.write('\nBelief vector ' + str(count) + ' ' + str(belief_vectors[index]))
			count +=1


		belief_vectors_non_zero_file.close()



	





