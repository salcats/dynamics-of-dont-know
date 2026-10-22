# Imports
import itertools
import numpy as np
import math
from utilities import inconsistency_measure
from utilities import exclusive_inconsistency_measure

import networkx as NX


# Global variables

# Classes

## Class to extract useful data
class DataExtraction():

	def __init__(self,adaptive_voter_model,exclusive):

		self.adaptive_voter_model = adaptive_voter_model

		self.graph = adaptive_voter_model.graph

		self.exclusive = exclusive


	def find_average_degree(self):

		average_degree = np.mean([self.graph.degree(x) for x in self.graph.nodes()])

		return average_degree

	def find_average_inconsistency(self):
		
		node_neighbours = [NX.all_neighbors(self.graph,node) for node in self.graph.nodes()]

		if self.exclusive:
			node_inconsistency =  [np.mean(np.asarray([exclusive_inconsistency_measure(self.graph.node[x],self.graph.node[i]) for i in node_neighbours[x]])) for x in range(1,len(self.graph.nodes()))]
		else:
			node_inconsistency =  [np.mean(np.asarray([inconsistency_measure(self.graph.node[x],self.graph.node[i],self.adaptive_voter_model.language_size) for i in node_neighbours[x]])) for x in range(1,len(self.graph.nodes()))]

		average_node_inconsistency = np.mean(np.asarray(node_inconsistency))

		if math.isnan(average_node_inconsistency):
			average_node_inconsistency = 0.0

		return average_node_inconsistency

	def unique_states(self,states):

		unique_states = []
		for state in states:
			if state not in unique_states:
				unique_states.append(state)

		return unique_states


	def find_prop_active_links(self):

		all_links = self.graph.edges()

		if self.exclusive:
			inert_links = [x for x in all_links if exclusive_inconsistency_measure(self.graph.node[x[0]],self.graph.node[x[1]]) == 0]
		else:
			inert_links = [x for x in all_links if inconsistency_measure(self.graph.node[x[0]],self.graph.node[x[1]],self.adaptive_voter_model.language_size) == 0]

		active_links = len(all_links) - len(inert_links)

		if len(all_links) != 0:
			prop_active_links = float(active_links)/float(len(all_links))
		else:
			prop_active_links = 0


		# Return number of active links or proportion of active links
		return prop_active_links


	def find_average_payoff(self):

		payoff = [self.graph.node[node]['payoff'] for node in self.graph.nodes()]

		average_payoff = np.mean(payoff)

		return average_payoff






# Script

#if __name__ = "__main__":