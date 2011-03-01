"""
This is the core module for pyga.

Here are the basic vanilla components; genes and a GA.
Other variations are sub-classes of these.


"""

import random


class Gene(object):
    """"
    This is the base class for Gene objects. These do not 
    represent a specific gene on one chromosme, rather
    it representes all possible genes that exist at that
    position - the different alleles (values).
    """

    def __init__(self, values=(None,)):
        """
        To initialize, simply pass the list of possible values.
        This will be kept for later mutation between them.
        """
        self.values = values

    def randomize(self, rng=None, old=None):
        if rng == None:
            rng = random.Random()
        values = self.values
        #when we randomize, we want to make sure we actually change
        #otherwise the net real mutation rate is not the same as 
        #the specified gross mutation rate
        #If there are a larger number of values, this may be an
        #inefficient way to do it.
        if old is not None:
            values = [x for x in values if x != old]
        return rng.choice(values)
    
    def __repr__(self):
        """
        Simple string representation to aid debugging.
        """
        return "<"+str(self.values)+">"

class GeneticAlg(object):
    """
    Base class for the GA itself. 
    """
    def __init__(self, size, generations, chromosomepattern, chromosomecount, survival, rng=None):
        """
        Constructor to create a GA.
        Currently, this also starts it running, which is probably a bad idea.
        
        TODO: describe parameters
        """
        self.size = size
        self.generations = generations
        self.generationno = 0
        self.chromosomepattern = chromosomepatterns
        self.chromosomecount = chromosomecount 
        self.survival = survival
        if rng is None:
            self.rng = random.Random()
        else:
            self.rng = rng
        self.population = [self.genomemake() for x in xrange(self.size)]
        self.score_population()

        while self.generationno < self.generations:
            #Should do some sort of progress bar here, if run from terminal
            self.generationno += 1
            self.evol_population()
            self.score_population()
    
    def genomemake(self):
        genome = []
        for i in xrange(self.chromosomecount):
            genome.append(tuple((genepattern.randomize(rng = self.rng) for genepattern in self.chromosomepattern)))
        return tuple(genome)

    def genomechange(self, genome):
        genomeout = []
        for chromosome in genome:
            chromosomeout = []
            for gene, genepattern in zip(chromosome, self.chromosomepattern):
                if random.random() < 1.0/len(chromosome): #this is mutationrate, avg of one per chromosome
                    chromosomeout.append(genepattern.randomize(rng = self.rng, old = gene))
                else:
                    chromosomeout.append(gene)
            genomeout.append(tuple(chromosomeout))
        return tuple(genomeout)

    def write_scores(self, filename):
        outfile = open(filename, 'w')
        for score, genome in self.scores:
            outfile.write(str(score))
            outfile.write('\t')
            outfile.write(str(genome))
            outfile.write('\n')

    def score_population(self):
        scores = [self.fitness_function(x) for x in self.population]
        #to randomize the order of tied individuals a random
        #number is assigned to each one. when sorted, this
        #random number will break ties. Odds of picking
        #two random floats the same is v. v. small
        rand = [self.rng.random() for x in self.population]
        self.scores = zip(scores, rand, self.population)
        self.scores.sort()
        #throw away the random number now that it is sorted
        self.scores = [(x[0], x[2]) for x in self.scores]

    def evol_population(self):
        assert len(self.scores) == len(self.population)
        survivecount = int(len(self.scores)*self.survival)
        #ensure there is at least one survivor
        if survivecount < 1:
            survivecount = 1
            
        survived = self. scores[:survivecount]
        killed = self.scores[survivecount:]
        assert len(survived) + len(killed) == len(population)
        #we should kill something or there is no room for births
        assert len(killed) > 0
        
        newgenomes = []
        parents = []
        
        #see what survived to go to the next generation
        for fitness, genome in tuple(survived):
            #fitnesses below the minimal score are gross
            #malformations - such as invalid data or other
            #very bad things. 
            #if this is the best we can do then we might
            #as well try things at random to find a better
            #area of the fitness landscape
            if fitness <= 0:
                newgenomes.append(self.genomemake())
            else:
                newgenomes.append(genome)
                #parents.append(genome)
                #best genomes have more chance to reproduce
                parents = parents + parents + [genome]

        #replace the dead with new individuals
        for i in xrange(len(killed)):
            if len(parents) == 0:
                #if none of the parents were worthy, generate
                #new random individual
                newgenomes.append(self.genomemake())
            else:
                #mutate a random parent
                #more sucessfull parents have more chance to be picked
                newgenomes.append(self.genomechange(random.choice(parents)))
            
        assert len(newgenomes) == len(self.population)    
        self.population = newgenomes
            
