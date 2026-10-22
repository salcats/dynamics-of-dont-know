# Imports
import numpy as np 
import itertools
import networkx as nx
import argparse
import time
from matplotlib import pyplot as plt

# Global variables

# Classes

class odeGenerator():

	def __init__(self,number_of_actions = 2):

		self.number_of_actions = number_of_actions

		# Generate all possible belief state vectors
		self.belief_states = [0.0,0.5,1.0]
		self.belief_state_vectors = list(itertools.product(self.belief_states,repeat = self.number_of_actions))

		# Create graph structure for storing information

		self.graph = nx.DiGraph()
		self.graph.add_nodes_from(self.belief_state_vectors)


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

		transition_products = [x for x in itertools.product(*transition_product_list)]

		return transition_products



	# This could be parallelised to improve performance 

	def add_transitions_to_graph(self,belief_state_vector):

		cartesian_product = self.cartesian_product(belief_state_vector)

		cartesian_product.remove(belief_state_vector)

		for state in cartesian_product:

			transition_products = self.transition_products(belief_state_vector,state)

			self.graph.add_edge(belief_state_vector,state, transition_states = transition_products)


	def add_all_transitions_to_graph(self):


		for belief_state_vector in self.belief_state_vectors:

			self.cartesian_product(belief_state_vector)

			self.add_transitions_to_graph(belief_state_vector)




# Script

if __name__ == "__main__":

	argument_parse = argparse.ArgumentParser()

	argument_parse.add_argument('-a','--actions',help = "number of actions")

	args = vars(argument_parse.parse_args())

	number_actions = int(args['actions'])

	running_time_list = []

	for action in range(number_actions):


		ode_generator = odeGenerator(action)

		start_time = time.time()
		ode_generator.add_all_transitions_to_graph()
		time_taken = time.time()-start_time
		running_time_list.append(time_taken)



	plt.plot(range(number_actions),running_time_list)
	plt.xlabel('Number of actions')
	plt.ylabel('Time taken (s) ')
	plt.show()


	#print ode_generator.graph.out_edges((0.0,0.0))[0]
	#print ode_generator.graph.edge[ode_generator.graph.out_edges((0.0,0.0))[0][0]][ode_generator.graph.out_edges((0.0,0.0))[0][1]]['transition_states']

	

## TO DO:

# Produce the ODE's from the network structure
# Look into 