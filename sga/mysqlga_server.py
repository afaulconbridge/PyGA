try:
    import cPickle as pickle
except ImportError:
    import pickle
import zlib
import time

import MySQLdb as mysqldb

from sga import GeneticAlg


class MySQLGeneticAlg(GeneticAlg):

    def __init__(self, servername, username, password, database, *args, **kwargs):
            
        #connect to db
        self.conn = mysqldb.connect(host=servername, user=username, passwd=password, db=database)
        cursor = self.conn.cursor()
                
        #create the tables if they dont exist
        cursor.execute("""CREATE TABLE IF NOT EXISTS pyga (
    searchid INT UNSIGNED, 
    generationid INT UNSIGNED, 
    individualid INT UNSIGNED, 
    genome BLOB, 
    fitness BLOB,
    status INT,
    PRIMARY KEY (searchid, generationid, individualid)
);""")
        
        self.get_searchid()
        
        self.starttime = int(time.time())

        super(MySQLGeneticAlg, self).__init__(*args, **kwargs)

    @property
    def funcblob(self):
        try:
            return self._funcblob
        except AttributeError:
            self._funcblob = zlib.compress(pickle.dumps(self.fitness_function))
            return self.funcblob
            

    def get_searchid(self):

        #assign searchid to be one more than the max in the database
        cursor = self.conn.cursor()
        cursor.execute("""SELECT max(searchid) FROM pyga""")
        result = cursor.fetchone()
        if result is None or result[0] is None:
            self.searchid = 1
        else:
            self.searchid = result[0]+1

    def score_population(self):
        
        cursor = self.conn.cursor()
        cursor.execute("""BEGIN;""")
        #put it in the database
        for i in xrange(len(self.population)):
            genome = self.population[i]
            blob = zlib.compress(pickle.dumps(genome))
            cursor.execute("""INSERT INTO pyga SET searchid=%s, 
    generationid=%s, 
    individualid=%s, 
    genome=%s, 
    fitness=%s,
    status=0;""", (self.searchid, self.generationno, i, blob, self.funcblob))    
        cursor.execute("""COMMIT;""")
        
        #wait until all have been done
        done = None
        while done < len(self.population):
            time.sleep(1)
            cursor.execute("""SELECT count(*) FROM pyga WHERE searchid=%s AND generationid=%s AND status=-1;""", (self.searchid, self.generationno))
            done = cursor.fetchone()[0]
            
            now = int(time.time())
            elapsed = now-self.starttime
            days = elapsed // (24*60*60)
            hours = (elapsed // (60*60)) % 24
            minutes = (elapsed // 60) % 60
            seconds = elapsed % 60
            
            print days, hours, minutes, seconds, self.generationno, done
            
        #now get them back
        
        cursor.execute("""SELECT fitness, individualid, genome FROM pyga WHERE searchid=%s AND generationid=%s AND status=-1 ORDER BY individualid;""", (self.searchid, self.generationno))
        self.scores = []
        result = cursor.fetchone()
        while result is not None:
            fitblob, i, genomeblob = result
            assert i == len(self.scores), (i, self.scores)
            fitness = pickle.loads(zlib.decompress(fitblob))
            genome = pickle.loads(zlib.decompress(genomeblob))
            assert genome == self.population[i]
            self.scores.append(fitness)
            result = cursor.fetchone()
        
        #To randomize the order of tied individuals a random
        #float is assigned to each one. When sorted, this
        #random number will break ties, not population position.
        #Odds of picking two random floats the same is v. v. small.
        rand = (self.rng.random() for x in self.population)
        self.scores = sorted(zip(self.scores, rand, self.population), reverse=True)
        #throw away the random number now that it is sorted
        self.scores = tuple(((x[0], x[2]) for x in self.scores))



