#fudge to use this version because its not installed
#TODO remove
import sys
import os.path
sys.path.append(os.path.abspath("."))

import pyga

"""
The problem is this:

You work in a pet shop. A customer
buys a parrot. 

Given that the parrot cost 26.38, the 
customer gave you a 50.00 note, and your till
contains only 17 x 100, 63 x 50p, 12 x 20p, 
and 142 x 2p coins, which coins should you give
to the customer in change?
"""

if __name__=="__main__":
    #create a fitness function
    #will be passed a genome as the parameter
    #should return an integer or float > 0.0
    def coins_fitness(genome):
        total = 0
        total += 100*genome[0][0]
        total +=  50*genome[0][1]
        total +=  20*genome[0][2]
        total +=   2*genome[0][3]
        error = abs(2638 - total)
        #because high fittness means better
        #need to subtract error from a perfect score
        fitness = 10000 - error
        return fitness
    
    
    #create a genome template
    #should be tuple of tuples of pyga.Gene
    #one chromosome
    #   number of 1.00 coins
    #   number of   50p coins
    #   number of   20p coins
    #   number of    2p coins
    genome = ((pyga.Gene(range(17)), pyga.Gene(range(63)), pyga.Gene(range(12)), pyga.Gene(range(142)) ),)
    
    ga = pyga.GeneticAlg(100, 1000, genome, coins_fitness)
    
    print "Best fitness:", ga.scores[0][0]
    print "Best genome:", ga.scores[0][1]
    #now express the results in a framework that is relevant to the problem
    print "1.00 coins:", ga.scores[0][1][0][0]
    print "  50 coins:", ga.scores[0][1][0][1]
    print "  20 coins:", ga.scores[0][1][0][2]
    print "   2 coins:", ga.scores[0][1][0][3]
    print "Error:", 10000 - ga.scores[0][0]
