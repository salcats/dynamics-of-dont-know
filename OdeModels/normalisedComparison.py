#Imports

#Global variables

#Classes

class NormalisedComparison():


	def __init__(self):




	def consensus_operator(self,belief_state_1,belief_state_2):


		if belief_state_1 == 0.0 and belief_state_2 == 0.0:
			consensus_outcome = [0.0]
		elif belief_state_1== 0.0 and belief_state_2 == 0.5:
			consensus_outcome = [0.0]
		elif belief_state_1== 0.0 and belief_state_2 == 1.0:
			consensus_outcome = [0.5]	
		elif belief_state_1 == 0.5 and belief_state_2 == 0.0:
			consensus_outcome = [0.0]
		elif belief_state_1 == 0.5 and belief_state_2 == 0.5:
			consensus_outcome = [0.5]
		elif belief_state_1 == 0.5 and belief_state_2 == 1.0:
			consensus_outcome = [1.0]
		elif belief_state_1 == 1.0 and belief_state_2 == 0.0:
			consensus_outcome = [0.5]
		elif belief_state_1 == 1.0 and belief_state_2 == 0.5:
			consensus_outcome = [1.0]
		elif belief_state_1 == 1.0 and belief_state_2 == 1.0:
			consensus_outcome = [1.0]


		return consensus_outcome


	def normalised_consensus(self,belief_state_vector_1,belief_state_vector_2):

		consensus = [self.consensus_operator(belief_state_vector_1[x],belief_state_vector_2[x]) for x in range(len(belief_state_vector_1))]
		
		
