# Imports
from adaptiveVoterModel import AdaptiveVoterModel
from exclusiveAdaptiveVoterModel import ExclusiveAdaptiveVoterModel
from dataExtraction import DataExtraction
from dataVisualisation import DataVisualisation
from dataVisualisation import plot_mode_1
from dataVisualisation import plot_mode_2
from dataVisualisation import plot_mode_3
from dataVisualisation import plot_mode_4
from dataVisualisation import plot_mode_5
from utilities import unique_states
from matplotlib import pyplot as plt
import argparse
import random as RD
import numpy as np
import os
import csv
import time
import networkx as NX
from collections import Counter

# Global variables

# Classes

class AdaptiveVoterRunner():

	def __init__(self):

		pass
		

	def run_mode_1(self,binary_model,agents,language_size,simulation_time,rewiring_rate,opinion_adoption_rate,random_state_change_rate,threshold,draw,zealots,exclusive):


		if exclusive == 1:

			adaptive_voter_model = ExclusiveAdaptiveVoterModel(number_agents,language_size,threshold,binary_model,zealots)

		else:

			adaptive_voter_model = AdaptiveVoterModel(number_agents,language_size,threshold,binary_model,zealots)



		data_extraction = DataExtraction(adaptive_voter_model,exclusive)

		data_visualisation = DataVisualisation(adaptive_voter_model)

		running_time = 0.0
		
		initial_states = [adaptive_voter_model.graph.node[x]['state'] for x in range(adaptive_voter_model.number_of_agents)]

		initial_distinct_states = unique_states(initial_states)

		initial_number_distinct_states = len(initial_distinct_states)

		if exclusive == 1:
			agent_vagueness = [float(len(adaptive_voter_model.graph.node[x]['state'])/adaptive_voter_model.language_size) for x in range(adaptive_voter_model.number_of_agents)]
		else:
			agent_vagueness = [float(adaptive_voter_model.graph.node[x]['state'].count(0.5))/adaptive_voter_model.language_size for x in range(adaptive_voter_model.number_of_agents)]
		
		initial_average_vagueness = np.sum(agent_vagueness)/adaptive_voter_model.number_of_agents

		initial_average_degree = data_extraction.find_average_degree()

		initial_average_inconsistency = data_extraction.find_average_inconsistency()

		initial_prop_active_links = data_extraction.find_prop_active_links()

		initial_average_payoff = data_extraction.find_average_payoff()

		worst_payoff = adaptive_voter_model.minimum_payoff
		diff_payoff = abs(adaptive_voter_model.maximum_payoff-worst_payoff)

		number_distinct_states_list = [initial_number_distinct_states]
		average_vagueness_list = [initial_average_vagueness]
		average_degree_list = [initial_average_degree]
		average_inconsistency_list = [initial_average_inconsistency]
		prop_active_links_list = [initial_prop_active_links]
		prop_average_payoff_list = [float(abs(initial_average_payoff-worst_payoff)/diff_payoff)]
		time_list = [running_time]
		rates = np.zeros((3))


		fragmentation_count = 0
		consensus_count = 0
		

		while running_time < simulation_time:

			number_links = len(adaptive_voter_model.graph.edges())
			rates[0] = (rewiring_rate) * number_links
			rates[1] = (opinion_adoption_rate) * number_links
			rates[2] = (random_state_change_rate) * number_agents


			## Inversion generating method from Monto Carlo theory
			# Define unit rate poisson process for each node to become active
		
			total_rate = np.sum(rates)

			random_1 = RD.random()
			random_2 = RD.random()

			running_time += np.log(1/random_1)/total_rate

			select_event = np.searchsorted(np.cumsum(rates),random_2*total_rate)

			adaptive_voter_model.step(select_event)

			states = [adaptive_voter_model.graph.node[x]['state'] for x in range(adaptive_voter_model.number_of_agents)]

			distinct_states = unique_states(states)

			number_distinct_states = len(distinct_states)

			if exclusive == 1:
				agent_vagueness = [float(len(adaptive_voter_model.graph.node[x]['state'])/adaptive_voter_model.language_size) for x in range(adaptive_voter_model.number_of_agents)]
			else:
				agent_vagueness = [float(adaptive_voter_model.graph.node[x]['state'].count(0.5))/adaptive_voter_model.language_size for x in range(adaptive_voter_model.number_of_agents)]
		
			average_vagueness = np.sum(agent_vagueness)/adaptive_voter_model.number_of_agents

			average_degree = data_extraction.find_average_degree()

			average_inconsistency = data_extraction.find_average_inconsistency()

			prop_active_links = data_extraction.find_prop_active_links()

			prop_average_payoff = float(abs(data_extraction.find_average_payoff()-worst_payoff)/diff_payoff)

			number_distinct_states_list.append(number_distinct_states)

			average_vagueness_list.append(average_vagueness)

			average_degree_list.append(average_degree)

			average_inconsistency_list.append(average_inconsistency)

			prop_active_links_list.append(prop_active_links)

			prop_average_payoff_list.append(prop_average_payoff)

			time_list.append(running_time)

			number_connected_components = NX.number_connected_components(adaptive_voter_model.graph)

			if (prop_active_links == 0.0) and (fragmentation_count == 0) and number_connected_components > 1:
				time_to_steady_state = running_time
				fragmentation_count += 1
				break
			elif prop_active_links == 0.0 and number_connected_components == 1 and consensus_count == 0:
				time_to_steady_state = running_time
				consensus_count += 1
				break




		final_number_distinct_states = number_distinct_states_list[-1]
		final_average_vagueness = average_vagueness_list[-1]
		final_average_degree = average_degree_list[-1]
		final_average_inconsistency = average_inconsistency_list[-1]
		final_prop_active_links = prop_active_links_list[-1]
		final_prop_average_payoff = prop_average_payoff_list[-1]
		
		states = [adaptive_voter_model.graph.node[x]['state'] for x in range(adaptive_voter_model.number_of_agents)]
		
		number_connected_components = NX.number_connected_components(adaptive_voter_model.graph)

		connected_component_subgraphs = NX.connected_component_subgraphs(adaptive_voter_model.graph)

		number_nodes_in_subgraphs = [len(x.nodes()) for x in connected_component_subgraphs]

		maximum_subgraph_size = max(number_nodes_in_subgraphs)

		average_size_of_subgraph =  np.mean(number_nodes_in_subgraphs)
		
		variance_of_subgraph_size = np.var(number_nodes_in_subgraphs)

		#data_visualisation.draw_network()

		if draw == 1:
			plot_mode_1(time_list,number_distinct_states_list,average_vagueness_list,average_degree_list,average_inconsistency_list,prop_active_links_list,threshold,states)


			print '\nFinal statistics ... '
			print '\nNumber of distinct valuations: ', final_number_distinct_states
			print '\nAverage vagueness: ', final_average_vagueness
			print '\nAverage degree: ',final_average_degree
			print '\nAverage inconsistency: ', final_average_inconsistency
			print '\nProportion of links that are active: ', final_prop_active_links
			print '\nTime to fragmenation: ', time_to_fragmentation
			print '\nState distribution: ', Counter(tuple(x) for x in states)
			print '\nAverage size of subgraph: ', average_size_of_subgraph
			print '\nVariance of subgraph size: ', variance_of_subgraph_size
			print '\nMaximum subgraph size: ', maximum_subgraph_size
		

			distinct_states = [list(state) for state in Counter(tuple(x) for x in states)]
			distinct_state_count = [count for count in Counter(tuple(x) for x in states).values()]

			plt.figure()
			plt.bar(range(len(distinct_states)), distinct_state_count, align='center', alpha=0.5)	
			plt.xlabel('Belief state index')
			plt.ylabel('Number of nodes in this belief state')
			plt.tight_layout()
			plt.savefig(trial_directory +  '/belief_states.tiff')
			
			data_visualisation.draw_network()

		## This is temporary		
		if fragmentation_count == 0 and consensus_count == 0:
			time_to_steady_state = 0

		return [final_number_distinct_states, final_average_vagueness, final_average_degree, final_average_inconsistency,final_prop_active_links, fragmentation_count, average_size_of_subgraph,variance_of_subgraph_size,maximum_subgraph_size, consensus_count, final_prop_average_payoff,time_to_steady_state]


	def run_sim_mode_2(self,binary_model,agents,language_size,simulation_time,rewiring_rate,opinion_adoption_rate,random_state_change_rate,threshold_lower_bound,threshold_upper_bound,zealots,exclusive):

		number_iterations = 10
		threshold_range = np.linspace(threshold_lower_bound,threshold_upper_bound,10)

		data_array_total = np.zeros((number_iterations,10,12))

		time_taken_list = []
		iterate_count = 0
		for iterate in range(number_iterations):
			start_time = time.time()
			threshold_count = 0
			data_array_iterate = np.zeros((10,12))
			for threshold in threshold_range:


				data_output = self.run_mode_1(binary_model,agents,language_size,simulation_time,rewiring_rate,opinion_adoption_rate,random_state_change_rate,threshold,0,zealots,exclusive)		
				
				data_array_iterate[threshold_count,:]  = data_output
				threshold_count += 1

			data_array_total[iterate_count] = data_array_iterate
			iterate_count += 1
			fraction_complete = float(iterate_count)/float(number_iterations)

			print 'Fraction of runs completed: ' + str(fraction_complete)
			time_taken = time.time()-start_time
			time_taken_list.append(time_taken)

			predicted_time_left = (number_iterations-iterate_count)*np.mean(time_taken_list)
			predicted_time_left = np.round(predicted_time_left,2)
			print 'Estimated time till completion: ' + str(predicted_time_left)


		return data_array_total

	def run_mode_2(self,agents,language_size,simulation_time,rewiring_rate,opinion_adoption_rate,random_state_change_rate,threshold_lower_bound,threshold_upper_bound,zealots,exclusive):


		threshold_range = np.linspace(threshold_lower_bound,threshold_upper_bound,10)

		ternary_model_data = self.run_sim_mode_2(0,agents,language_size,simulation_time,rewiring_rate,opinion_adoption_rate,random_state_change_rate,threshold_lower_bound,threshold_upper_bound,zealots,exclusive)
		binary_model_data = self.run_sim_mode_2(1,agents,language_size,simulation_time,rewiring_rate,opinion_adoption_rate,random_state_change_rate,threshold_lower_bound,threshold_upper_bound,zealots,exclusive)

	
	
		if rewiring_rate == 0 and random_state_change_rate == 0 and zealots == 0:
			base_path = '/home/sal/Documents/Project/Python_Data/Voter_Models/Exclusive/mode_2_voter/'
		elif rewiring_rate == 0 and random_state_change_rate != 0 and zealots ==0:
			base_path  = '/home/sal/Documents/Project/Python_Data/Voter_Models/Exclusive/mode_2_noisy_voter/'
		elif rewiring_rate != 0 and random_state_change_rate == 0 and zealots == 0:
			base_path = '/home/sal/Documents/Project/Python_Data/Voter_Models/Exclusive/mode_2_adap_voter/'
		elif rewiring_rate != 0 and random_state_change_rate != 0 and zealots == 0:
			base_path  = '/home/sal/Documents/Project/Python_Data/Voter_Models/Exclusive/mode_2_noisy_adap_voter/'
		elif rewiring_rate == 0 and random_state_change_rate == 0 and zealots != 0:
			base_path = '/home/sal/Documents/Project/Python_Data/Voter_Models/Exclusive/mode_2_voter_zealots/'
		elif rewiring_rate != 0 and random_state_change_rate == 0 and zealots != 0:
			base_path = '/home/sal/Documents/Project/Python_Data/Voter_Models/Exclusive/mode_2_adap_voter_zealots/'


		folders = 0
		for _, dirnames, filenames in os.walk(base_path):
			folders += len(dirnames)

		trial_number = folders+ 1
		trial_directory = base_path + 'trial_' + str(trial_number)

		
		if not os.path.exists(trial_directory):
			os.makedirs(trial_directory)
			print 'Creating directory...'
		

		plot_mode_2(ternary_model_data,binary_model_data,threshold_range,trial_directory)


		parameter_file = open(trial_directory + '/parameters.csv','w')

		parameter_file.write('Number of agents: ' + str(agents))
		parameter_file.write('\nLanguage size: ' + str(language_size))
		parameter_file.write('\nSimulation time: ' + str(simulation_time))
		parameter_file.write('\nRewiring rate: ' + str(rewiring_rate))
		parameter_file.write('\nOpinion adoption rate: ' + str(opinion_adoption_rate))

		parameter_file.close()

	def run_mode_3(self,binary_model,agents,language_size_lower_bound,language_size_upper_bound,simulation_time,rewiring_rate,opinion_adoption_rate,threshold_lower_bound,threshold_upper_bound):

		threshold_range = np.linspace(threshold_lower_bound,threshold_upper_bound,10)
		language_size_range = np.linspace(language_size_lower_bound,language_size_upper_bound,(language_size_upper_bound-language_size_lower_bound)/5 + 1)
		data_array = np.zeros((len(language_size_range),10,10))

		time_taken_list = []

		language_size_range = [5,10,50]
		language_size_count = 0
		for language_size in language_size_range:
			language_size = int(language_size)
			threshold_count = 0
			for threshold in threshold_range:
				start_time = time.time()
				data_output = self.run_mode_1(binary_model,agents,language_size,simulation_time,rewiring_rate,opinion_adoption_rate,threshold,0)
				data_array[language_size_count,threshold_count,:]  = data_output
				threshold_count += 1	

				time_taken = time.time()-start_time
				time_taken_list.append(time_taken)
				predicted_time_left = (len(threshold_range)*len(language_size_range)-(threshold_count+(language_size_count*10)))*np.mean(time_taken_list)
				predicted_time_left = np.round(predicted_time_left,2)
				print 'Estimated time till completion: ' + str(predicted_time_left)


			language_size_count += 1
			fraction_complete = float(language_size_count)/float(len(language_size_range))
			print 'Fraction of runs completed: ' + str(fraction_complete)


		if binary_model:

			base_path = '/home/sal/Documents/Project/Python_Data/Adaptive_Voter_Model/mode_3_binary/'

		elif not binary_model:

			base_path = '/home/sal/Documents/Project/Python_Data/Adaptive_Voter_Model/mode_3_ternary/'


		folders = 0
		for _, dirnames, filenames in os.walk(base_path):
			folders += len(dirnames)

		trial_number = folders+ 1

		if binary_model:
			trial_directory = '/home/sal/Documents/Project/Python_Data/Adaptive_Voter_Model/mode_3_binary/' + 'trial_' + str(trial_number)

		elif not binary_model:
			trial_directory = '/home/sal/Documents/Project/Python_Data/Adaptive_Voter_Model/mode_3_ternary/' + 'trial_' + str(trial_number)

		if not os.path.exists(trial_directory):
			os.makedirs(trial_directory)
			print 'Creating directory...'


		plot_mode_3(data_array,threshold_range,trial_directory,language_size_range)

		parameter_file = open(trial_directory + '/parameters.csv','w')

		parameter_file.write('Number of agents: ' + str(agents))
		parameter_file.write('\nSimulation time: ' + str(simulation_time))
		parameter_file.write('\nRewiring rate: ' + str(rewiring_rate))
		parameter_file.write('\nOpinion adoption rate: ' + str(opinion_adoption_rate))

		parameter_file.close()

	def run_mode_4(self,binary_model,number_agents,language_size,simulation_time,rewiring_rate_lower_bound,rewiring_rate_upper_bound,opinion_adoption_rate,threshold):

		rewiring_range = np.linspace(rewiring_rate_lower_bound,rewiring_rate_upper_bound,10)

		data_array = np.zeros((10,10))

		time_taken_list = []

		rewiring_count = 0
		for rewiring_rate in rewiring_range:
			start_time  = time.time()
			data_output = self.run_mode_1(binary_model,number_agents,language_size,simulation_time,rewiring_rate,opinion_adoption_rate,threshold,0)
			data_array[rewiring_count,:]  = data_output
			rewiring_count += 1

			fraction_complete = float(rewiring_count)/float(len(rewiring_range))
			print 'Fraction of runs completed: ' + str(fraction_complete)

			time_taken = time.time()-start_time
			time_taken_list.append(time_taken)

			predicted_time_left = (len(rewiring_range)-rewiring_count)*np.mean(time_taken_list)
			predicted_time_left = np.round(predicted_time_left,2)

			print 'Estimated time till completion: ' + str(predicted_time_left)


		if binary_model:

			base_path = '/home/sal/Documents/Project/Python_Data/Adaptive_Voter_Model/mode_4_binary/'

		elif not binary_model:

			base_path = '/home/sal/Documents/Project/Python_Data/Adaptive_Voter_Model/mode_4_ternary/'


		folders = 0
		for _, dirnames, filenames in os.walk(base_path):
			folders += len(dirnames)

		trial_number = folders+ 1

		if binary_model:
			trial_directory = '/home/sal/Documents/Project/Python_Data/Adaptive_Voter_Model/mode_4_binary/' + 'trial_' + str(trial_number)

		elif not binary_model:
			trial_directory = '/home/sal/Documents/Project/Python_Data/Adaptive_Voter_Model/mode_4_ternary/' + 'trial_' + str(trial_number)

		if not os.path.exists(trial_directory):
			os.makedirs(trial_directory)
			print 'Creating directory...'

		plot_mode_4(data_array,rewiring_range,trial_directory)


		parameter_file = open(trial_directory + '/parameters.csv','w')

		parameter_file.write('Number of agents: ' + str(number_agents))
		parameter_file.write('\nLanguage size: ' + str(language_size))
		parameter_file.write('\nSimulation time: ' + str(simulation_time))
		parameter_file.write('\nOpinion adoption rate: ' + str(opinion_adoption_rate))
		parameter_file.write('\nThreshold: ' + str(threshold))

		parameter_file.close()


	def run_mode_5(self,binary_model,number_agents,language_size,simulation_time,rewiring_rate_lower_bound,rewiring_rate_upper_bound,opinion_adoption_rate,threshold_lower_bound,threshold_upper_bound):

		threshold_range = np.linspace(threshold_lower_bound,threshold_upper_bound,10)
		rewiring_range = np.linspace(rewiring_rate_lower_bound,rewiring_rate_upper_bound,10)

		data_array = np.zeros((len(threshold_range),2))

		time_taken_list = []

		threshold_count = 0
		for threshold in threshold_range:
			threshold = float(threshold)
			rewiring_count = 0
			for rewiring_rate in rewiring_range:
				start_time = time.time()
				data_output = self.run_mode_1(binary_model,number_agents,language_size,simulation_time,rewiring_rate,opinion_adoption_rate,threshold,0)
				prop_active_links = data_output[4]
				if prop_active_links == 0.0:
					data_array[threshold_count,0] = threshold
					data_array[threshold_count,1] = rewiring_rate
					break
				rewiring_count += 1
				
				time_taken = time.time()-start_time
				time_taken_list.append(time_taken)
				predicted_time_left = (len(rewiring_range)*len(threshold_range)-(rewiring_count+(threshold_count*10)))*np.mean(time_taken_list)
				predicted_time_left = np.round(predicted_time_left,2)
				print 'Estimated time till completion: ' + str(predicted_time_left)

			threshold_count += 1
			fraction_complete = float(threshold_count)/(float(len(threshold_range)))
			print 'Fraction of runs completed: ' + str(fraction_complete)



		if binary_model:

			base_path = '/home/sal/Documents/Project/Python_Data/Adaptive_Voter_Model/mode_5_binary/'

		elif not binary_model:

			base_path = '/home/sal/Documents/Project/Python_Data/Adaptive_Voter_Model/mode_5_ternary/'




		folders = 0
		for _, dirnames, filenames in os.walk(base_path):
			folders += len(dirnames)

		trial_number = folders+ 1

		if binary_model:
			trial_directory = '/home/sal/Documents/Project/Python_Data/Adaptive_Voter_Model/mode_5_binary/' + 'trial_' + str(trial_number)

		elif not binary_model:
			trial_directory = '/home/sal/Documents/Project/Python_Data/Adaptive_Voter_Model/mode_5_ternary/' + 'trial_' + str(trial_number)

		if not os.path.exists(trial_directory):
			os.makedirs(trial_directory)
			print 'Creating directory...'


		plot_mode_5(data_array,trial_directory)

		parameter_file = open(trial_directory + '/parameters.csv','w')

		parameter_file.write('Number of agents: ' + str(number_agents))
		parameter_file.write('\nSimulation time: ' + str(simulation_time))
		parameter_file.write('\nOpinion adoption rate: ' + str(opinion_adoption_rate))
		parameter_file.write('\nLanguage size: ' + str(language_size))


		parameter_file.close()

		
# Script

if __name__ == "__main__":

	argument_parse = argparse.ArgumentParser()

	argument_parse.add_argument('-m','--mode',help = "mode of operation:\n  1 - Fixed threshold,agents,language size \n 2 - Parameter sweep on threshold (fixed agents,language size) \n 3 - Parameter sweep on threshold and language size (fixed agents) \n 4 - Fragmentation transition as function of rewiring rate (single threshold value) \n 5 - Fragmenation transition - what rewiring probability is required for different thresholds\n")
	argument_parse.add_argument('-ag','--agents',help = "number of agents")
	argument_parse.add_argument('-ll','--language_size_lower',help = "lower bound on language size")
	argument_parse.add_argument('-lu','--language_size_upper',help = "upper bound on language size")
	argument_parse.add_argument('-st','--sim_time',help = "simulation time")
	argument_parse.add_argument('-rl','--rewiring_lower',help = "lower bound on rewiring rate")
	argument_parse.add_argument('-ru','--rewiring_upper',help = "upper bound on rewiring rate")
	argument_parse.add_argument('-or','--opinion_adoption',help = "opinion adoption rate")
	argument_parse.add_argument('-sc','--state_change',help = "random_state_change rate")
	argument_parse.add_argument('-tl','--thresh_lower',help = "lower bound on interaction threshold")
	argument_parse.add_argument('-tu','--thresh_upper',help = "upper bound on interaction threshold")
	argument_parse.add_argument('-z','--zealots',help = "include/do not include zealots who do not change their opinion (number zealots/0 )")
	argument_parse.add_argument('-e','--exclusive',help = "1/0 - exclusive/not exclusive propositions")


	args = vars(argument_parse.parse_args())

	mode = int(args['mode'])
	number_agents = int(args['agents'])
	language_size_lower_bound = int(args['language_size_lower'])
	language_size_upper_bound = int(args['language_size_upper'])
	simulation_time = float(args['sim_time'])
	rewiring_rate_lower_bound = float(args['rewiring_lower'])
	rewiring_rate_upper_bound = float(args['rewiring_upper'])
	random_state_change_rate = float(args['state_change'])
	opinion_adoption_rate = float(args['opinion_adoption'])
	threshold_lower_bound = float(args['thresh_lower'])
	threshold_upper_bound = float(args['thresh_upper'])
	zealots = float(args['zealots'])
 	exclusive = float(args['exclusive'])

	if mode == 1:

		# Fixed threshold, agents, language size

		adaptive_voter_runner = AdaptiveVoterRunner()
		adaptive_voter_runner.run_mode_1(number_agents,language_size_lower_bound,simulation_time,rewiring_rate_lower_bound,opinion_adoption_rate,random_state_change_rate,threshold_lower_bound,1,zealots)

   
	elif mode == 2:

		# Fixed agents, language size and parameter sweep on threshold

		adaptive_voter_runner = AdaptiveVoterRunner()
		adaptive_voter_runner.run_mode_2(number_agents,language_size_lower_bound,simulation_time,rewiring_rate_lower_bound,opinion_adoption_rate,random_state_change_rate,threshold_lower_bound,threshold_upper_bound,zealots,exclusive)

	elif mode == 3:

		# Fixed agents, parameter sweep on language size and threshold

		if binary == 1:
			binary_model = True
		elif binary == 0:
			binary_model = False

		adaptive_voter_runner = AdaptiveVoterRunner()
		adaptive_voter_runner.run_mode_3(binary_model,number_agents,language_size_lower_bound,language_size_upper_bound,simulation_time,rewiring_rate_lower_bound,opinion_adoption_rate,threshold_lower_bound,threshold_upper_bound)


	elif mode == 4:	

		# Steady states as function of rewiring rate (fixed language size, threshold, agents)
   		## How can we plot this for consensus and fragmentation transition?

		if binary == 1:
			binary_model = True
		elif binary == 0:
			binary_model = False

		adaptive_voter_runner = AdaptiveVoterRunner()
		adaptive_voter_runner.run_mode_4(binary_model,number_agents,language_size_lower_bound,simulation_time,rewiring_rate_lower_bound,rewiring_rate_upper_bound,opinion_adoption_rate,threshold_lower_bound)

   	elif mode == 5:

   		# What rewiring rate causes steady state for different interaction thresholds

   		## How can we plot this for consensus and fragmentation transition?
		if binary == 1:
			binary_model = True
		elif binary == 0:
			binary_model = False

		adaptive_voter_runner = AdaptiveVoterRunner()
		adaptive_voter_runner.run_mode_5(binary_model,number_agents,language_size_lower_bound,simulation_time,rewiring_rate_lower_bound,rewiring_rate_upper_bound,opinion_adoption_rate,threshold_lower_bound,threshold_upper_bound)
   





