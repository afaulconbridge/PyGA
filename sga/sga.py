"""
PyGA
====

This is the core module for pyga.

Here are the basic vanilla components; Gene and a GeneticAlgorithm
Other variations are sub-classes of these.

"""

import random


class Gene(object):
    """
    This is the base class for Gene objects. These do not 
    represent a specific gene on one chromosme, rather
    it representes all possible genes that exist at that
    position - the different alleles (values).
    """

    def __init__(self, values=(None,)):
        """
        To initialize, simply pass the list of possible values.
        This will be kept for later mutation between them.
        
        Recommended to pass a tuple to avoid accidental modification.
        This is not enforced as you may want to change values over time
        and this way it can be done, if not recommended
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
    Base class for the Genetic Algorithm itself. 
    """
    def __init__(self, populationsize, generations, genomepattern, fitness_function, survival=0.1, rng=None, avgmutations=1.0, mutationrate = None):
        """
        Constructor to create a GA.
        Currently, this also starts it running, which is probably a bad idea.
        
        TODO: describe parameters
        """
        assert populationsize > 0
        self.populationsize = populationsize
        assert generations > 0
        self.generations = generations
        self.generationno = 0
        assert len(genomepattern) > 0
        assert len(genomepattern[0]) > 0
        self.genomepattern = genomepattern
        
        #in python, functions are object too
        #therefore rather than calling the passed
        #function now, we store it so it can 
        #be called in the future
        self.fitness_function = fitness_function
        
        #proportion survival rate
        #higher is quicker optimization, but may be premature.
        #best value depends on particular problem
        assert survival > 0.0 and survival < 1.0
        self.survival = survival
        
        #mutation is expressed either as a probability per gene
        #or as an average per genome per generation
        if mutationrate is None:
            assert avgmutations is not None
            #avgmutations is the number of mutations per genome per generation on average
            self.mutationrate = float(sum((len(x) for x in genomepattern))) / avgmutations
            
        if rng is None:
            self.rng = random.Random()
        else:
            self.rng = rng
        self.population = [self.genome_make() for x in xrange(populationsize)]
        self.score_population()

        while self.generationno < self.generations:
            #Should do some sort of progress bar here, if run from terminal
            self.generationno += 1
            self.evol_population()
            self.score_population()
    
    def genome_make(self):
        """
        Creates a new genome based on self.chromosomepatterns.
        Uses the selfs random number generator, which may have
        been seeded.
        
        Genome return is a tuple of tuples of alleles. 
        """
        genome = ()
        for chromosomepattern in self.genomepattern:
            chromosome = ()
            for genepattern in chromosomepattern:
                #adding tuples concatenates
                chromosome = chromosome + (genepattern.randomize(rng = self.rng),)
            genome = genome + (chromosome,)
        return genome

    def genome_mutate(self, genome):
        """
        Returns a mutated copy of a genome. 
        Genome must match self.chromosomepatterns, which it will do if created via
        self.genomemake or self.genomemutate.
        Mutation rate is based on self.mutationrate.
        
        This does not do cross-over.
        This does not do duplication/deletion, and can't unless changes are made to 
        self.chromosomepatterns too.
        """
        genomeout = ()
        for chromosome, chromosomepattern in zip(genome, self.genomepattern):
            chromosomeout = ()
            for gene, genepattern in zip(chromosome, chromosomepattern):
                if random.random() < self.mutationrate:
                    chromosomeout = chromosomeout + (genepattern.randomize(rng = self.rng, old = gene),)
                else:
                    chromosomeout = chromosomeout + (gene, )
            genomeout = genomeout + (chromosomeout,)
        return genomeout

    def write_scores(self, filename):
        """
        Dumps current generation to disk.
        Fomat is tab-separated between score and genome.
        """
        outfile = open(filename, 'w')
        for score, genome in self.scores:
            outfile.write(str(score))
            outfile.write('\t')
            outfile.write(str(genome))
            outfile.write('\n')

    def score_population(self):
        """
        Calculates the fitness of each individual in the population.
        Then sorts the population in descending fitness order.
        Ties are broken randomly.
        
        Rather than returning the scores, it sets the self.scores variable
        This it to discourage repeated fitness calculations becaue it can
        be a computationally expensive process.
        
        The genomes of the current generation are stored with the scores.
        This is to make it easy to see which genome got which score, rather
        than assuming self.population and self.scores have the same ordering.
        """
        scores = [self.fitness_function(x) for x in self.population]
        #To randomize the order of tied individuals a random
        #float is assigned to each one. When sorted, this
        #random number will break ties, not population position.
        #Odds of picking two random floats the same is v. v. small.
        rand = (self.rng.random() for x in self.population)
        self.scores = sorted(zip(scores, rand, self.population), reverse=True)
        #throw away the random number now that it is sorted
        self.scores = tuple(((x[0], x[2]) for x in self.scores))

    def evol_population(self):
        """
        Evolves a new generation of the population based on
        the fitness values calculated by score_population. 
        
        Replaces self.population with the new generation.
        """
        assert len(self.scores) == len(self.population)
        survivecount = int(len(self.scores)*self.survival)
        #ensure there is at least one survivor
        if survivecount < 1:
            survivecount = 1
            
        survived = self. scores[:survivecount]
        killed = self.scores[survivecount:]
        assert len(survived) + len(killed) == len(self.population)
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
                newgenomes.append(self.genome_make())
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
                newgenomes.append(self.genome_make())
            else:
                #mutate a random parent
                #more sucessfull parents have more chance to be picked
                newgenomes.append(self.genome_mutate(random.choice(parents)))
            
        assert len(newgenomes) == len(self.population)    
        self.population = newgenomes
            
