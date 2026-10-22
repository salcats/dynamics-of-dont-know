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
from scipy.linalg import eig


# Classes


'''
This class shows that the solutions to the odes generated from a binary model with n = 2 (and generalises) 
never reach consensus on one belief state. There are infinitely many equilibria where x(0)x(3) = x(1)(4). 
This class iterates the simulation and determines whether the equilibrium that is found in each iteration is
either a stable,unstable, saddle or undetermined by the linear part. This is achieved using the analytic jacobian.
It shows that the stability of most of the equilibria cannot be determined from the linear part, some are saddle and there
are some that are stable. The equilibria are never completely unstable.
'''


class OdeGeneratorBinaryInvestigation():

	def __init__(self,iterations,plot_option):

		self.iterations = iterations
		self.number_states = 4
		self.consensus_counts = np.zeros(self.number_states)
		self.number_actions = 2
		self.belief_state_vectors = [(0,0),(0,1),(1,0),(1,1)]
		self.plot_option = plot_option
		

	def ode_runner(self):

		steady_state_check = 0
		count = 0
		unstable_equilibria = 0
		stable_equilibria = 0
		saddle_equilibria = 0

		for iteration in range(self.iterations):

			t,soln = ode_solver(self.number_states)
			
			if  np.round(soln[-1,0]*soln[-1,3],6) == np.round(soln[-1,1]*soln[-1,2],6):
				steady_state_check += 1

			x1  = soln[-1,0]
			x2  = soln[-1,1]
			x3  = soln[-1,2]
			x4  = soln[-1,3]

			a = np.zeros((4,4))

			a[0,:] = (-x4,x3,x2,-x1)
			a[1,:] = (x4, -x3,-x2,x1)
			a[2,:] = (x4, -x3,-x2,x1)
			a[3,:] = (-x4,x3,x2,-x1)
			eigenvalues = eig(a)[0]

			second_count = 0
			eigen_count = 0
			positive_count = 0
			negative_count = 0

		
	
			for i in range(len(eigenvalues)):
				if eigenvalues[i] == 0.0:
					count+=1
					eigen_count += 1
					break	

			if eigen_count == 0:

				for i in range(len(eigenvalues)):
					if eigenvalues[i] > 0:
						positive_count +=1 
					elif eigenvalues[i] < 0:
						negative_count += 1

		

			
		
			if positive_count == 4:
				unstable_equilibria += 1

				if self.plot_option == 1:
					plt.figure()
					for x in range(np.power(2,self.number_actions)):
						plt.plot(t,soln[:,x])
						plt.xlabel('Time (s)')
						plt.ylabel('Proportion of agents')
						plt.title('Unstable equilibrium')
					plt.show()
					quit()

			
			elif negative_count == 4:

				if self.plot_option == 2:
					plt.figure()
					for x in range(np.power(2,self.number_actions)):
						plt.plot(t,soln[:,x])
						plt.xlabel('Time (s)')
						plt.ylabel('Proportion of agents')
						plt.title('Stable equilibrium')
					plt.show()
					quit()


				stable_equilibria += 1

			elif positive_count >=1 and negative_count >= 1:

				if self.plot_option  == 3:
					plt.figure()
					for x in range(np.power(2,self.number_actions)):
						plt.plot(t,soln[:,x])
						plt.xlabel('Time (s)')
						plt.ylabel('Proportion of agents')
						plt.title('Saddle equilibrium')
					plt.show()
					quit()

				saddle_equilibria += 1


		print "Fraction of steady state checks that match with analytic work: " + str(float(steady_state_check)/float(iterations))
		print "Number of realisations with non-hyperbolic equilibria: " + str(count)
		print "Number of realisations with unstable equilibria: " + str(unstable_equilibria)
		print "Number of realisations with stable equilibria: " + str(stable_equilibria)
		print "Number of realisations with saddle equilibria: " + str(saddle_equilibria)









def f(X,t):
	dotX = zeros_like(X)

	dotX[0] = -0.5*(X[0]*X[3] - X[1]*X[2]) 
	dotX[1] = -0.5*(X[1]*X[2]- X[0]*X[3]) 
	dotX[2] = -0.5*(X[1]*X[2] - X[0]*X[3])
	dotX[3] = -0.5*(X[0]*X[3]- X[1]*X[2])
 
	return dotX

def ode_solver(number_states):

	Xo = np.random.normal(1./number_states,0.05,number_states)
	
	Xo = [float(i)/sum(Xo) for i in Xo]

	t =  np.linspace(0, 100., 1000) 

	start_time = time.time()

	soln	 = odeint(f, Xo, t)

	time_taken = time.time()-start_time

	final_proportions = [soln[-1,x] for x in range(number_states)]
	
	consensus_index = final_proportions.index(max(final_proportions))


	return t,soln


# Script

if __name__ == "__main__":

	argument_parse = argparse.ArgumentParser()

	argument_parse.add_argument('-it','--iterations',help = " number of iterations")
	argument_parse.add_argument('-p','--plot',help = " 1 (unstable) 2 (stable) 3 (saddle) ")

	args = vars(argument_parse.parse_args())

	iterations = int(args['iterations'])
	plot_option  = int(args['plot'])

	ode_binary_test = OdeGeneratorBinaryInvestigation(iterations,plot_option)

	ode_binary_test.ode_runner()
