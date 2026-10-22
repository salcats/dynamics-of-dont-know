# Simple Network Dynamics simulator in Python
#
# *** The Voter Model of Opinion Formation on a Network ***
#
# Copyright 2010-2013 Hiroki Sayama
# sayama@binghamton.edu

# Imports
import matplotlib
from matplotlib import pyplot as plt
import networkx as NX
import argparse
import random as RD
import pylab as PL
import numpy as np 
from numpy.random import uniform as uni
from utilities import unique_states
from utilities import exclusive_inconsistency_measure
import itertools
from itertools import count
import math


# Global variables

# Classes

## This is the exclusive proposition version

class ExclusiveAdaptiveVoterModel():

    def __init__(self, agents , prop_variables, threshold,binary_model,zealots):
        
        self.number_of_agents = agents
        self.language_size = prop_variables
        self.graph = NX.complete_graph(self.number_of_agents)
        self.threshold = threshold
        self.binary = binary_model
        self.number_of_zealots = zealots

        # Zealots - agents who refuse to change their opinion
        if self.number_of_zealots != 0:
            self.zealot_indices = [RD.choice(self.graph.nodes()) for x in range(int(self.number_of_zealots))]
        else:
            self.zealot_indices = []

        # Assign a payoff to each proposition
        self.proposition_payoffs = uni(-1,1,self.language_size).tolist()

        
        self.maximum_payoff = max(self.proposition_payoffs)
        self.minimum_payoff = min(min(self.proposition_payoffs),0)

        # Set representation of beliefs for mutually exclusive propositions
        # Set [1,2] = {<1,0,0>,<0,1,0>}

        base_set = set(range(1,self.language_size+1))
        permissible_states_ternary = [[set(y) for y in itertools.combinations(base_set,x)] for x in range(1,self.language_size+1)]
        permissible_states_ternary = list(itertools.chain.from_iterable(permissible_states_ternary))
        

        self.permissible_states_ternary = permissible_states_ternary
        self.permissible_states_binary = [set([y]) for y in range(1,self.language_size+1)]


        # Run ternary or binary mode
        if not self.binary:

            for node in self.graph.nodes_iter():
                belief_vector = RD.choice(self.permissible_states_ternary)
                self.graph.node[node]['state'] = belief_vector
                self.update_belief_payoff(self.graph.node[node])

        elif self.binary:

            for node in self.graph.nodes_iter():
                belief_vector = RD.choice(self.permissible_states_binary)
                self.graph.node[node]['state'] = belief_vector
                self.update_belief_payoff(self.graph.node[node])


    ## Update the belief payoffs for each node. 

    def update_belief_payoff(self,node):  

        belief_vector = node['state']

        if len(belief_vector) > 1:
            node['payoff'] = 0
        elif len(belief_vector) == 1:
            node['payoff'] = self.proposition_payoffs[list(belief_vector)[0]-1]


    ## Update rules for ternary and binary 

    def update_rule_ternary(self,listener_set,speaker_set): 

        # Find the intersection of the sets of beliefs
        set_intersection = listener_set & speaker_set

        # If the intersection is equal to the empty set then the consensus result is
        # the union otherwise the consensus result is the intersection
        if set_intersection == set([]):
            consensus_result = listener_set | speaker_set
        else:
            consensus_result = set_intersection

        return consensus_result


    # Basic model - choose one agent with equal probability, the consensus result is the belief of this agent 

    def update_rule_binary(self,listener_set,speaker_set):

        consensus_index = RD.choice([1,2])

        if consensus_index == 1:
            consensus_result = listener_set
        else:
            consensus_result = speaker_set

        return consensus_result
           

    # Find inconsistent links
    def find_inconsistent_links(self):

        all_links = self.graph.edges()

        inconsistent_links = [x for x in all_links if exclusive_inconsistency_measure(self.graph.node[x[0]],self.graph.node[x[1]]) >= self.threshold]

        return inconsistent_links


    # Find possible consistent links to one node
    def find_possible_consistent_links(self,node_id):

        all_links = self.graph.edges()

        possible_nodes = [x for x in self.graph.nodes() if exclusive_inconsistency_measure(self.graph.node[x],self.graph.node[node_id]) < self.threshold]

        if len(possible_nodes) != 0:

            possible_nodes.remove(node_id)
    
            possible_consistent_links = [(node_id,x) for x in possible_nodes]

        else:

            possible_consistent_links = []
        
        return possible_consistent_links

    
    # Rewiring event
    def rewiring_event(self):

        ### Modelling assumption: do remove just inconsistent links or any links
        # Find link
        links = self.find_inconsistent_links()
        #links = self.graph.edges()

        if len(links)!=0:
        
            # Find nodes associated with links

            node_payoffs = []
            count = 0

            for link in links:

                ### Modelling assumption: choose nodes prop to the difference between their respective payoffs
                node_payoff_sum = abs(np.subtract([self.graph.node[link[0]]['payoff'],self.graph.node[link[1]]['payoff']]))
                node_payoffs.append(node_payoff_sum)
                count+=1

            # Choose link with probabilities proportional to cummulative payoff

            if max(node_payoffs)==0 and min(node_payoffs)==0:
                link_id = np.random.choice(range(len(links)))   
            else:
                norm_node_payoffs = (node_payoffs-min(node_payoffs))/(max(node_payoffs)-min(node_payoffs))
                norm_node_payoffs = [float(i)/sum(norm_node_payoffs) for i in norm_node_payoffs]
                link_id = np.random.choice(range(len(links)),p = norm_node_payoffs)  

            link = links[link_id]

            node_ids = [x for x in link]
            self.graph.remove_edge(*link)

            # Choose one of the nodes that was part of this link with prob 1/2
            chosen_node = RD.choice(node_ids) 

            # Rewire this node to a new node that has a consistent belief

            link_list = self.find_possible_consistent_links(chosen_node)

            if len(link_list) != 0:

                link = RD.choice(link_list)

                self.graph.add_edge(*link)



    def opinion_adoption_event(self):

        ### Modelling assumption: does opinion adoption only happen on inconsisten links or on all links ( all links is better I think)
        #links = self.find_inconsistent_links()
        links = self.graph.edges()

        # Find nodes associated with inconsistent links

        node_payoffs = []
        count = 0

        if len(links) != 0 :
            for link in links:

                ### Modelling assumption: choose nodes prop to the difference between their respective payoffs
                node_payoff_sum = abs(np.subtract([self.graph.node[link[0]]['payoff'],self.graph.node[link[1]]['payoff']]))
                node_payoffs.append(node_payoff_sum)
                count+=1

            # Choose link with probabilities proportional to cummulative payoff

            if max(node_payoffs)==0 and min(node_payoffs)==0:
                link_id = np.random.choice(range(len(links)))   
            else:
                norm_node_payoffs = (node_payoffs-min(node_payoffs))/(max(node_payoffs)-min(node_payoffs))
                norm_node_payoffs = [float(i)/sum(norm_node_payoffs) for i in norm_node_payoffs]
                link_id = np.random.choice(range(len(links)),p = norm_node_payoffs)  

            link = links[link_id]

            node_ids = [x for x in link]

            listener_id =  RD.choice(node_ids)

        
            if len(self.graph.neighbors(listener_id)) != 0 and listener_id not in self.zealot_indices :
                
                speaker_id = RD.choice(self.graph.neighbors(listener_id))
                listener = self.graph.node[listener_id]
                speaker = self.graph.node[speaker_id]

                prior_listener_belief_vector = listener['state']
            
                speaker_belief_vector =speaker['state']

                if not self.binary:
                    posterior_listener_belief_vector = self.update_rule_ternary(prior_listener_belief_vector,speaker_belief_vector)
                elif self.binary:
                    posterior_listener_belief_vector = self.update_rule_binary(prior_listener_belief_vector,speaker_belief_vector) 

                listener['state'] = posterior_listener_belief_vector
                
                self.update_belief_payoff(listener)


    # Random state change event for the noisy voter model 
    def random_state_change_event(self):

        # Choose node at random 
        node_id = RD.choice(self.graph.nodes())
        node = self.graph.node[node]
        node_state = node['state']

        ### Modelling assumption: 

        ### If the state of the node is of the form <0,...,0,p_k,0...0> where 
        ### k is any index in range (1-N) then the random state change takes the union of this state
        ### with another random state of the same form i.e. p_k | p_i where is is chosen at random 
        ### from the set 1-N / k

        ### If the state of the node is any of form then the random state change manifests as
        ### the set difference between that state and a state of the form <0,...,0,p_k,0...0>
        ### where that state is chosen at random from the original set


        if len(node_state) == 1:
            # Choose proposition at random 
            proposition_choice = RD.choice(list(set(range(1,self.language_size+1)) - node_state))
            node['state'] = node_state | set([proposition_choice])
        else:
            proposition_choice  = RD.choice(list(node_state))
            node['state'] = node_state - set([proposition_choice])


    # Step the simulation forward one step
    def step(self,event):

        # event == 0 corresponds to rewiring event
        if event == 0:
                        
            self.rewiring_event()

        # event == 1 corresponds to opinion adopition event
        elif event == 1:

            self.opinion_adoption_event()

        # event == 3 corresponds to random state change

        elif event == 3:

            self.random_state_change_event()





   