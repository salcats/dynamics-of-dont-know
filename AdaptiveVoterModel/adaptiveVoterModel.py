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
from utilities import inconsistency_measure
import itertools
from itertools import count
import math


# Global variables

# Classes

## This is the non-exclusive proposition version

class AdaptiveVoterModel():

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
        positive_payoffs = [x for x in self.proposition_payoffs if x>=0]
        negative_payoffs = [x for x in self.proposition_payoffs if x<0]

        self.maximum_payoff = np.sum(positive_payoffs) - np.sum(negative_payoffs)
        self.minimum_payoff = -self.maximum_payoff


        # Run ternary or binary mode
        if not self.binary:

            for node in self.graph.nodes_iter():
                belief_vector = [RD.choice([0,0.5,1]) for x in range(self.language_size)]
                self.graph.node[node]['state'] = belief_vector
                self.update_belief_payoff(self.graph.node[node])

        elif self.binary:

            for node in self.graph.nodes_iter():
                belief_vector = [RD.choice([0,1]) for x in range(self.language_size)]
                self.graph.node[node]['state'] = belief_vector
                self.update_belief_payoff(self.graph.node[node])


    ## Update the belief payoffs for each node. This is calculated using an expression from paper
    ## by Lawry and Crosscombe.

    def update_belief_payoff(self,node):  

        belief_vector = node['state']

        additive_payoffs = [self.proposition_payoffs[x] for x in range(len(belief_vector)) if belief_vector[x]==1 ]
        reductive_payoffs = [self.proposition_payoffs[x] for x in range(len(belief_vector)) if belief_vector[x]==0]

        node['payoff'] = np.sum(additive_payoffs) - np.sum(reductive_payoffs)


    ## Encodes the logic of the consensus operator into a set of rules
    def update_rule(self,prop_var_listener,prop_var_speaker):

        if (prop_var_listener == 0.0 and prop_var_speaker == 0.0) or  (prop_var_listener == 0 and prop_var_speaker == 0.5):
            prop_var_listener = 0
        elif prop_var_listener == 0.0 and prop_var_speaker == 1:
            prop_var_listener = 0.5
        elif (prop_var_listener == 1 and prop_var_speaker == 0.5) or (prop_var_listener == 1 and prop_var_speaker == 1):
            prop_var_listener = 1
        elif prop_var_listener == 1 and prop_var_speaker == 0.0:
            prop_var_listener = 0.5
        elif prop_var_listener == 0.5 and prop_var_speaker == 1:
            prop_var_listener = 1
        elif prop_var_listener == 0.5 and prop_var_speaker == 0.0:
            prop_var_listener = 0.0
        elif prop_var_listener == 0.5 and prop_var_speaker ==0.5:
            prop_var_listener = 0.5

        return prop_var_listener


    ## Assign 1 or 0 with probability 1/2 ( not sure if this is a good model...)
    def update_rule_binary(self,prop_var_listener,prop_var_speaker):

        if (prop_var_listener == 0.0 and prop_var_speaker == 0.0):
            prop_var_listener = 0.0
        elif (prop_var_listener == 1.0 and prop_var_speaker == 1.0):
            prop_var_listener = 1.0
        elif (prop_var_listener == 0.0 and prop_var_speaker == 1.0) or (prop_var_listener == 1.0 and prop_var_speaker == 0.0):
            possible_set = [0.0 , 1.0]
            prop_var_listener = RD.choice(possible_set)

        return prop_var_listener
           

    ## Find inconsistent links in the network
    def find_inconsistent_links(self):

        all_links = self.graph.edges()

        inconsistent_links = [x for x in all_links if inconsistency_measure(self.graph.node[x[0]],self.graph.node[x[1]], self.language_size) >= self.threshold]

        return inconsistent_links


    ## Find possible consistent links to a particular node
    def find_possible_consistent_links(self,node_id):

        all_links = self.graph.edges()

        possible_nodes = [x for x in self.graph.nodes() if inconsistency_measure(self.graph.node[x],self.graph.node[node_id],self.language_size) < self.threshold]

        if len(possible_nodes) != 0:

            possible_nodes.remove(node_id)
    
            possible_consistent_links = [(node_id,x) for x in possible_nodes]

        else:

            possible_consistent_links = []
        
        return possible_consistent_links

    
    ## Rewiring event 
    def rewiring_event(self):

        # Find links
        
        ### Modelling assumption: do remove just inconsistent links or any links
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


    ## Opnion adoption event
    def opinion_adoption_event(self):

    	### Modelling assumption: (do we choose opinion adoption events to occur only along inconsistent links or on any links)
        #links = self.find_inconsistent_links()
        links = self.graph.edges()

        # Find nodes associated with these links

        node_payoffs = []
        count = 0
        for link in links:

        	### Modelling assumption: choose nodes prop to the difference between their respective payoffs
            node_payoff_sum = abs(np.subtract([self.graph.node[link[0]]['payoff'],self.graph.node[link[1]]['payoff']]))
            node_payoffs.append(node_payoff_sum)
            count+=1

        # Choose link with probabilities proportional to cummulative payoff

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
                posterior_listener_belief_vector = [self.update_rule(prior_listener_belief_vector[x],speaker_belief_vector[x]) for x in range(len(prior_listener_belief_vector))]
            elif self.binary:
                posterior_listener_belief_vector = [self.update_rule_binary(prior_listener_belief_vector[x],speaker_belief_vector[x]) for x in range(len(prior_listener_belief_vector))]

            listener['state'] = posterior_listener_belief_vector
            
            self.update_belief_payoff(listener)


    ## Random state change event for the noisy voter model 
    def random_state_change_event(self):

        # Choose node at random 
        node_id = RD.choice(self.graph.nodes())
        node = self.graph.node[node]
        node_state = node['state']

        # Choose proposition at random 
        proposition_choice = RD.choice(range(self.language_size))

        ### This is a modelling assumption (just modify one proposition)

        # Randomly change the state of this proposition
        current_proposition_var = set([node_state[proposition_choice]])
        state_set = set([0,0.5,1])
        belief_choice = RD.choice(list(state_set - current_proposition_var))
        updated_proposition_var = belief_choice

        node['state'][proposition_choice] = updated_proposition_var


    ## Step the simulation one event
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





   