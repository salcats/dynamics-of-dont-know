# Imports
import numpy as np 
import itertools
import argparse
import time
from matplotlib import pyplot as plt
from scipy.integrate import odeint
from scipy import zeros_like
import os
from utilities import unique_states


# Global variables

# Classes


#INCOMPLETE --  HOW LONG DOES IT TAKE TO REACH CONSENSUS ? OUTPUT the time when the proportion of agents is 1 for one state etc and then average over the iterations

'''
This class generates and then solves the odes for the ternary case of n actions. In this class the
actions are not considered to be mutually exclusive. 
'''

class odeGeneratorTernary():

	def __init__(self,number_of_actions = 2):

		self.number_of_actions = number_of_actions

		# Generate all possible belief state vectors
		self.belief_states = [0.0,0.5,1.0]
		self.belief_vectors = list(itertools.product(self.belief_states,repeat = self.number_of_actions))

	

	def permissible_transitions(self,belief_state):


		if belief_state == 0.0:
			transition_states = [0.0, 0.5]
		elif belief_state == 0.5:
			transition_states = [0.0,0.5,1.0]
		else:
			transition_states = [0.5,1.0]

		return transition_states


	def cartesian_product(self,belief_state_vector):

		joint_permissible_transitions = [self.permissible_transitions(x) for x in belief_state_vector]

		cartesian_product = [x for x in itertools.product(*joint_permissible_transitions)]

		cartesian_product.remove(belief_state_vector)

		cartesian_product = [self.belief_vectors.index(x) for x in cartesian_product]


		return cartesian_product


	def consensus_operator(self,belief_state_1,belief_state_2):

		if belief_state_1 == 0.0 and belief_state_2 == 0.0:
			transition_states = [0.0,0.5]
		elif belief_state_1== 0.0 and belief_state_2 == 0.5:
			transition_states = [1.0]
		elif belief_state_1 == 0.5 and belief_state_2 == 0.0:
			transition_states = [0.0]
		elif belief_state_1 == 0.5 and belief_state_2 == 0.5:
			transition_states = [0.5]
		elif belief_state_1 == 0.5 and belief_state_2 == 1.0:
			transition_states = [1.0]
		elif belief_state_1 == 1.0 and belief_state_2 == 0.5:
			transition_states = [0.0]
		elif belief_state_1 == 1.0 and belief_state_2 == 1.0:
			transition_states = [0.5,1.0]


		return transition_states


	def transition_products(self,belief_state_vector_1,belief_state_vector_2):


		transition_product_list  = [self.consensus_operator(belief_state_vector_1[x],belief_state_vector_2[x]) for x in range(len(belief_state_vector_1))]

		transition_products = [self.belief_vectors.index(x) for x in itertools.product(*transition_product_list)]
	
	
		return transition_products

	
	def generate_transition_data_structure(self):


		transition_data_structure =  {self.belief_vectors.index(belief_state_vector): {x : self.transition_products(belief_state_vector,self.belief_vectors[x]) for x in self.cartesian_product(belief_state_vector)} for belief_state_vector
				in self.belief_vectors}


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


	ode_generator = odeGeneratorTernary(language_size)
	
	start_time = time.time()

	global data_structure

	data_structure = ode_generator.generate_transition_data_structure()

	time_taken = time.time()-start_time

	print 'Time taken to generate odes: ', time_taken

	number_states = np.power(3,language_size)

	consensus_counts = np.zeros(number_states)

	def f(X,t):

		# Includes conservation law 
		dotX = zeros_like(X)


		for belief_vector_index in range(number_states-1):

			reductive_indices = [x for x in itertools.chain.from_iterable(data_structure[belief_vector_index].values())]
			additive_indices = []

			for belief_vector, outgoings in data_structure.iteritems():
				for key in outgoings.keys():
					if key == belief_vector_index:
						additive_indices.append([[belief_vector,x] for x in outgoings[key]])
				
					
			additive_indices = [item for sublist in additive_indices for item in sublist]
			
			#additive_indices = [set(x) for x in additive_indices]
			#additive_indices = [list(item) for item in set(frozenset(item) for item in additive_indices)]
	
			

			dotX[belief_vector_index] -=  X[belief_vector_index]*(sum([X[x] for x in reductive_indices]))
			dotX[belief_vector_index] += sum([X[additive[0]]*X[additive[1]] for additive in additive_indices])

		dotX[-1] = -sum(dotX)

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

		for x in range(np.power(3,language_size)):
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

		base_path = '/home/sal/Documents/Project/Python_Data/ODE/Not_Exclusive/Ternary/'

		folders = 0
		for _, dirnames, filenames in os.walk(base_path):
			folders += len(dirnames)

		trial_number = folders+ 1

		trial_directory = '/home/sal/Documents/Project/Python_Data/ODE/Not_Exclusive/Ternary/' + 'trial_' + str(trial_number)

		if not os.path.exists(trial_directory):
			os.makedirs(trial_directory)
			print 'Creating directory...'

		average_time_to_consensus = np.round(np.mean(consensus_times),2)


		plt.bar(possible_consensus_states, consensus_counts, align='center', alpha=0.5)	
		plt.xlabel('Belief state')
		plt.ylabel('Times consensus reached on this belief state')
		consensus_counts = consensus_counts.tolist()

		plt.title('Average conensus reached on belief vector: '+ str(ode_generator.belief_vectors[consensus_counts.index(max(consensus_counts))]) + '\nAverage time to reach consensus: ' +str(average_time_to_consensus))
		
		plt.savefig(trial_directory +  '/ode_ternary.tiff')

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

