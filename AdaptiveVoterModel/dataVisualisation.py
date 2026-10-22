# Imports
import networkx as NX
from matplotlib import pyplot as plt
from utilities import unique_states
from matplotlib.legend_handler import HandlerLine2D
import numpy as np

# Global variables

# Classes

class DataVisualisation():

	def __init__(self,adaptive_voter_model):

		self.graph = adaptive_voter_model.graph

	def draw_network(self):
		
		current_distinct_states = len(unique_states([self.graph.node[node]['state'] for node in self.graph.nodes()]))

		plt.figure()

		for state in range(current_distinct_states):
			state_group = [x for x in self.graph.nodes() if self.graph.node[x]['state'] == unique_states(NX.get_node_attributes(self.graph,'state').values())[state]]
			for node in state_group:
				self.graph.node[node]['state_id'] = state

		node_colours = [self.graph.node[node_id]['state_id'] for node_id in self.graph.nodes()]

		positions = NX.spring_layout(self.graph)

		edges = NX.draw_networkx_edges(self.graph, positions, alpha=0.5)
		nodes = NX.draw_networkx_nodes(self.graph, positions, nodelist=self.graph.nodes(), node_color=node_colours, 
		with_labels=False, node_size=100, cmap=plt.cm.Blues)

		plt.show()



# Functions


def plot_mode_1(time_list,number_distinct_states_list,average_vagueness_list,average_degree_list,average_inconsistency_list,prop_active_links_list,threshold):

	f, axarr = plt.subplots(5, sharex=True)
	axarr[0].semilogy(time_list,number_distinct_states_list)
	axarr[0].set_ylabel('Distinct valuations')
	axarr[0].set_xlabel('Time (s)')
	axarr[1].plot(time_list,average_vagueness_list)
	axarr[1].set_ylabel('Average vagueness')
	axarr[1].set_xlabel('Time (s)')
	axarr[2].plot(time_list,average_degree_list)
	axarr[2].set_ylabel('Average degree')
	axarr[2].set_xlabel('Time (s)')
	axarr[3].plot(time_list,average_inconsistency_list)
	axarr[3].set_ylabel('Average inconsistency')
	axarr[3].set_xlabel('Time (s)')
	axarr[4].plot(time_list,prop_active_links_list)
	axarr[4].set_ylabel('Proportion of active links')
	axarr[4].set_xlabel('Time (s)')
	
	axarr[0].set_title('Threshold: ' + str(threshold))

	plt.show()

def plot_mode_2(ternary_model_data,binary_model_data,threshold_range,trial_directory):

	t_mean_distinct_states, t_mean_average_vagueness, t_mean_average_degree, t_mean_average_inconsistency, t_mean_prop_active_links, t_mean_average_size_of_subgraph,t_mean_variance_of_subgraph_size,t_mean_maximum_subgraph_size, t_mean_prop_avg_payoff, t_mean_time_to_steady_state = mean_model_data(ternary_model_data)

	b_mean_distinct_states, b_mean_average_vagueness, b_mean_average_degree, b_mean_average_inconsistency, b_mean_prop_active_links, b_mean_average_size_of_subgraph,b_mean_variance_of_subgraph_size,b_mean_maximum_subgraph_size, b_mean_prop_avg_payoff, b_mean_time_to_steady_state = mean_model_data(binary_model_data)

	t_std_distinct_states, t_std_average_vagueness, t_std_average_degree, t_std_average_inconsistency, t_std_prop_active_links, t_std_average_size_of_subgraph,t_std_variance_of_subgraph_size,t_std_maximum_subgraph_size, t_std_prop_avg_payoff, t_std_time_to_steady_state = std_model_data(ternary_model_data)

	b_std_distinct_states, b_std_average_vagueness, b_std_average_degree, b_std_average_inconsistency, b_std_prop_active_links, b_std_average_size_of_subgraph,b_std_variance_of_subgraph_size,b_std_maximum_subgraph_size, b_std_prop_avg_payoff, b_std_time_to_steady_state = std_model_data(binary_model_data)

	t_frag_count, t_cons_count = frag_cons_model_data(ternary_model_data)
	b_frag_count, b_cons_count = frag_cons_model_data(binary_model_data)

	'''
	plt.figure()
	plt.plot(threshold_range,distinct_states)
	plt.xlabel('Threshold')
	plt.ylabel('Distinct valuations')
	plt.tight_layout()
	plt.savefig(trial_directory +  '/distinct_valuations.jpeg')

	plt.figure()
	plt.plot(threshold_range,average_vagueness)
	plt.xlabel('Threshold')
	plt.ylabel('Average vagueness')
	plt.tight_layout()
	plt.savefig(trial_directory +  '/average_vagueness.jpeg')

	plt.figure()
	plt.plot(threshold_range,average_degree)
	plt.xlabel('Threshold')
	plt.ylabel('Average number of links')
	plt.tight_layout()
	plt.savefig(trial_directory +  '/average_degree.jpeg')

	plt.figure()
	plt.plot(threshold_range,average_inconsistency)
	plt.xlabel('Threshold')
	plt.ylabel('Average inconsistency')
	plt.tight_layout()
	plt.savefig(trial_directory +  '/average_inconsistency.jpeg')
	

	plt.figure()
	plt.plot(threshold_range,average_inconsistency)
	plt.xlabel('Threshold')
	plt.ylabel('Proportion of active links')
	plt.tight_layout()
	plt.savefig(trial_directory +  '/proportion_active_links.jpeg')

	'''
	
	
	fig = plt.figure()
	ax = fig.add_subplot(111)
	threshold_range = range(len(threshold_range))
	threshold_range_ticks = [float(x)/10 for x in threshold_range]
	ind = np.arange(len(threshold_range))

	width = 0.35	   # the width of the bars

	barlist_t = ax.bar(ind, t_mean_time_to_steady_state,width, align='center', alpha=0.5,yerr = t_std_time_to_steady_state,error_kw=dict(ecolor='gray', lw=2, capsize=5, capthick=2))	
	barlist_b = ax.bar(ind+width, b_mean_time_to_steady_state,width, align='center', alpha=0.5,yerr = b_std_time_to_steady_state,error_kw=dict(ecolor='gray', lw=2, capsize=5, capthick=2))	

	consensus_legend_count = 0
	fragmentation_legend_count = 0
	for ss in range(10):
		a = np.argmax([t_frag_count[ss],t_cons_count[ss]])
		if a == 1:
			barlist_t[ss].set_color('r')
			if consensus_legend_count == 0:
				barlist_t[ss].set_label('Consensus state (ternary model)')
				consensus_legend_count += 1
		elif a == 0:
			barlist_t[ss].set_color('b')
			if fragmentation_legend_count == 0:
				barlist_t[ss].set_label('Fragmented state (ternary model)')
				fragmentation_legend_count += 1

	consensus_legend_count = 0
	fragmentation_legend_count = 0
	for ss in range(10):
		a = np.argmax([b_frag_count[ss],b_cons_count[ss]])
		if a == 1:
			barlist_b[ss].set_color('m')
			if consensus_legend_count == 0:
				barlist_b[ss].set_label('Consensus state (binary model)')
				consensus_legend_count += 1
		elif a == 0:
			barlist_b[ss].set_color('g')
			if fragmentation_legend_count == 0:
				barlist_b[ss].set_label('Fragmented state (binary model)')
				fragmentation_legend_count += 1



	plt.xlabel('Inconsistency threshold',fontsize=20)
	plt.ylabel('Mean time to steady state (s)',fontsize = 20)
	plt.xticks(threshold_range,threshold_range_ticks)
	plt.legend()
	plt.tight_layout()
	figManager = plt.get_current_fig_manager()
	figManager.window.showMaximized()
	plt.savefig(trial_directory +  '/time_to_steady_state.jpeg')



	fig = plt.figure()
	ax = fig.add_subplot(111)
	ternary = plt.plot(threshold_range,t_mean_prop_avg_payoff,'r',label = 'Ternary model')
	binary = plt.plot(threshold_range,b_mean_prop_avg_payoff,'g',label  = 'Binary model')

	#plt.errorbar(threshold_range,t_mean_prop_avg_payoff, yerr=t_std_prop_avg_payoff,fmt='o', ecolor='r', capthick=2)
	#plt.errorbar(threshold_range,b_mean_prop_avg_payoff, yerr=b_std_prop_avg_payoff,fmt='o', ecolor='g', capthick=2)


	plt.xlabel('Inconsistency threshold', fontsize = 20)
	plt.ylabel('Mean proportion of optimal payoff', fontsize = 20)
	plt.xticks(threshold_range,threshold_range_ticks)
	plt.tight_layout()
	plt.legend()
	figManager = plt.get_current_fig_manager()
	figManager.window.showMaximized()
	plt.savefig(trial_directory +  '/prop_avg_payoff.jpeg')

	

	'''

	
	plt.figure()
	plt.plot(threshold_range,average_size_of_subgraph)
	plt.xlabel('Threshold')
	plt.ylabel('Average size of subgraph')
	plt.tight_layout()
	plt.savefig(trial_directory +  '/average_size_of_subgraph.jpeg')

	plt.figure()
	plt.plot(threshold_range,variance_of_subgraph_size)
	plt.xlabel('Threshold')
	plt.ylabel('Variance_of_subgraph_size')
	plt.tight_layout()
	plt.savefig(trial_directory +  '/variance_of_subgraph_size.jpeg')


	plt.figure()
	plt.plot(threshold_range,maximum_subgraph_size)
	plt.xlabel('Threshold')
	plt.ylabel('Maximum_subgraph_size')
	plt.tight_layout()
	plt.savefig(trial_directory +  '/maximum_subgraph_size.jpeg')


'''

def plot_mode_3(data_array,threshold_range,trial_directory,language_size_range):


	plt.figure()
	ax = plt.subplot(111)

	for language_size in range(len(language_size_range)):
		distinct_states = data_array[language_size,:,0]
		line, = plt.plot(threshold_range,distinct_states, label = '|L| : ' + str(language_size_range[language_size]))

	plt.xlabel('Threshold')
	plt.ylabel('Distinct valuations')
	plt.tight_layout()

	box = ax.get_position()
	ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
	ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

	plt.savefig(trial_directory +  '/distinct_valuations.jpeg')


	plt.figure()
	ax = plt.subplot(111)
	for language_size in range(len(language_size_range)):
		average_vagueness = data_array[language_size,:,1]
		line, = plt.plot(threshold_range,average_vagueness, label = '|L| : ' + str(language_size_range[language_size]))

	plt.xlabel('Threshold')
	plt.ylabel('Average vagueness')
	plt.tight_layout()
	
	box = ax.get_position()
	ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
	ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	
	plt.savefig(trial_directory +  '/average_vagueness.jpeg')


	plt.figure()
	ax = plt.subplot(111)
	for language_size in range(len(language_size_range)):
		average_degree = data_array[language_size,:,2]
		line, = plt.plot(threshold_range,average_degree, label = '|L| : ' + str(language_size_range[language_size]))

	plt.xlabel('Threshold')
	plt.ylabel('Average number of links')
	plt.tight_layout()

	box = ax.get_position()
	ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
	ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

	plt.savefig(trial_directory +  '/average_degree.jpeg')


	plt.figure()
	ax = plt.subplot(111)
	for language_size in range(len(language_size_range)):
		average_inconsistency = data_array[language_size,:,3]
		line, = plt.plot(threshold_range,average_inconsistency, label = '|L| : ' + str(language_size_range[language_size]))

	plt.xlabel('Threshold')
	plt.ylabel('Average inconsistency')
	plt.tight_layout()
	
	box = ax.get_position()
	ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
	ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

	plt.savefig(trial_directory +  '/average_inconsistency.jpeg')

	plt.figure()
	ax = plt.subplot(111)
	for language_size in range(len(language_size_range)):
		prop_active_links = data_array[language_size,:,5]
		line, = plt.plot(threshold_range,prop_active_links, label = '|L| : ' + str(language_size_range[language_size]))

	plt.xlabel('Threshold')
	plt.ylabel('Proportion of active links')
	plt.tight_layout()
	
	box = ax.get_position()
	ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
	ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

	plt.savefig(trial_directory +  '/proporition_active_links.jpeg')


	time_to_fragmentation = data_array[:,5]
	time_to_consensus = data_array[:,9]

	times_to_stationary = np.zeros((10,2))
	times_to_stationary[:,0] = time_to_fragmentation
	times_to_stationary[:,1] = time_to_consensus
	non_zero_indices_1 =  np.where(times_to_stationary != 0)[0]
	non_zero_indices_2 =  np.where(times_to_stationary != 0)[1]
	times_to_stationary = [times_to_stationary[non_zero_indices_1[x],non_zero_indices_2[x]] for x in range(len(non_zero_indices_1))]


	plt.figure()
	ax = plt.subplot(111)
	for language_size in range(len(language_size_range)):
		barlist = plt.bar(range(len(threshold_range)), times_to_stationary, align='center', alpha=0.5)	
		#line, = plt.plot(threshold_range,time_to_fragmentation, label = '|L| : ' + str(language_size_range[language_size]))
		for ss in range(len(non_zero_indices_1)):
			if non_zero_indices_2[ss] == 1:
				barlist[ss].set_color('r')
			elif non_zero_indices_2[ss] == 0:
				barlist[ss].set_color('b')
		plt.xlabel('Threshold')
		plt.ylabel('Time to steady state (s)')
		plt.title('Language_size = ' + str(language_size_range[language_size]))
		plt.tight_layout()
	
		box = ax.get_position()
		ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
		ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

		plt.savefig(trial_directory +  '/time_to_steady_state_l_' + str(language_size_range[language_size]) + '.jpeg')


	

	plt.figure()
	ax = plt.subplot(111)
	for language_size in range(len(language_size_range)):
		average_size_of_subgraph = data_array[language_size,:,6]
		line, = plt.plot(threshold_range,average_size_of_subgraph, label = '|L| : ' + str(language_size_range[language_size]))

	plt.xlabel('Threshold')
	plt.ylabel('Average size of subgraph')
	plt.tight_layout()
	
	box = ax.get_position()
	ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
	ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

	plt.savefig(trial_directory +  '/average_size_of_subgraph.jpeg')

	plt.figure()
	ax = plt.subplot(111)
	for language_size in range(len(language_size_range)):
		variance_of_subgraph_size = data_array[language_size,:,7]
		line, = plt.plot(threshold_range,variance_of_subgraph_size, label = '|L| : ' + str(language_size_range[language_size]))

	plt.xlabel('Threshold')
	plt.ylabel('Variance of subgraph size')
	plt.tight_layout()
	
	box = ax.get_position()
	ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
	ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

	plt.savefig(trial_directory +  '/variance_of_subgraph_size.jpeg')

	plt.figure()
	ax = plt.subplot(111)
	for language_size in range(len(language_size_range)):
		maximum_subgraph_size = data_array[language_size,:,8]
		line, = plt.plot(threshold_range,maximum_subgraph_size, label = '|L| : ' + str(language_size_range[language_size]))

	plt.xlabel('Threshold')
	plt.ylabel('Maximum subgraph size')
	plt.tight_layout()
	
	box = ax.get_position()
	ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
	ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

	plt.savefig(trial_directory +  '/maximum_subgraph_size.jpeg')


def plot_mode_4(data_array,rewiring_range,trial_directory):


	distinct_states = data_array[:,0]
	average_vagueness = data_array[:,1]
	average_degree = data_array[:,2]
	average_inconsistency = data_array[:,3]
	prop_active_links = data_array[:,4]
	time_to_fragmentation = data_array[:,5]
	time_to_consensus = data_array[:,9]

	plt.figure()
	plt.plot(rewiring_range,prop_active_links)
	plt.xlabel('Rewiring rate')
	plt.ylabel('Proportion of active links')
	plt.tight_layout()
	plt.savefig(trial_directory +  '/proportion_active_links.jpeg')

def plot_mode_5(data_array,trial_directory):


	threshold_range = data_array[:,0]
	steady_state_rewiring_rates = data_array[:,1]

	plt.figure()
	plt.plot(threshold_range,steady_staterewiring_rates)
	plt.xlabel('Threshold')
	plt.ylabel('Rewiring rate')
	plt.tight_layout()
	plt.savefig(trial_directory +  '/fragmentation.jpeg')



def mean_model_data(model_data):

	mean_distinct_states = np.mean([model_data[x][:,0] for x in range(10)],axis = 0)
	mean_average_vagueness = np.mean([model_data[x][:,1] for x in range(10)],axis = 0)
	mean_average_degree = np.mean([model_data[x][:,2] for x in range(10)],axis = 0)
	mean_average_inconsistency = np.mean([model_data[x][:,3] for x in range(10)],axis = 0)
	mean_prop_active_links = np.mean([model_data[x][:,4] for x in range(10)],axis = 0)
	mean_average_size_of_subgraph = np.mean([model_data[x][:,6] for x in range(10)],axis = 0)
	mean_variance_of_subgraph_size = np.mean([model_data[x][:,7] for x in range(10)],axis = 0)
	mean_maximum_subgraph_size = np.mean([model_data[x][:,8] for x in range(10)],axis = 0)
	mean_prop_avg_payoff = np.mean([model_data[x][:,10] for x in range(10)],axis = 0)
	mean_time_to_steady_state =  np.mean([model_data[x][:,11] for x in range(10)],axis = 0)

	return mean_distinct_states, mean_average_vagueness, mean_average_degree, mean_average_inconsistency, mean_prop_active_links, mean_average_size_of_subgraph,mean_variance_of_subgraph_size,mean_maximum_subgraph_size, mean_prop_avg_payoff, mean_time_to_steady_state


def std_model_data(model_data):

	std_distinct_states = np.std([model_data[x][:,0] for x in range(10)],axis = 0)

	std_average_vagueness = np.std([model_data[x][:,1] for x in range(10)],axis = 0)
	std_average_degree = np.std([model_data[x][:,2] for x in range(10)],axis = 0)
	std_average_inconsistency = np.std([model_data[x][:,3] for x in range(10)],axis = 0)
	std_prop_active_links = np.std([model_data[x][:,4] for x in range(10)],axis = 0)
	std_average_size_of_subgraph = np.std([model_data[x][:,6] for x in range(10)],axis = 0)
	std_variance_of_subgraph_size = np.std([model_data[x][:,7] for x in range(10)],axis = 0)
	std_maximum_subgraph_size = np.std([model_data[x][:,8] for x in range(10)],axis = 0)
	std_prop_avg_payoff = np.std([model_data[x][:,10] for x in range(10)],axis = 0)
	std_time_to_steady_state =  np.std([model_data[x][:,11] for x in range(10)],axis = 0)

	return std_distinct_states, std_average_vagueness, std_average_degree, std_average_inconsistency, std_prop_active_links, std_average_size_of_subgraph,std_variance_of_subgraph_size,std_maximum_subgraph_size, std_prop_avg_payoff, std_time_to_steady_state



def frag_cons_model_data(model_data):
	frag_count = np.sum([model_data[x][:,5] for x in range(10)],axis=0)
	cons_count = np.sum([model_data[x][:,9] for x in range(10)],axis=0)
	return frag_count, cons_count
# Script

#if __name__ = "__main__":