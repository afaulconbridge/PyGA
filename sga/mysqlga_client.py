try:
    import cPickle as pickle
except ImportError:
    import pickle
import zlib
import time
import argparse
import sys

import MySQLdb as mysqldb


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Genetic Algorithm MySQL Client.')
    parser.add_argument('path', help='path to add for libraries etc', default=".")
    parser.add_argument("servername", help="name of MySQL server")
    parser.add_argument("username", help="username of MySQL server")
    parser.add_argument("password", help="password of MySQL server")
    parser.add_argument("database", help="database of MySQL server")
    args = parser.parse_args()
    
    sys.path[0] =args.path
    
    #print "Using path", sys.path
    
    servername = args.servername
    username = args.username
    password = args.password
    database = args.database
    
    conn = mysqldb.connect(host=servername, user=username, passwd=password, db=database)
    cursor = conn.cursor()
    
    running = True
    while running:
        cursor.execute("SELECT * FROM pyga WHERE status=0")
        result = cursor.fetchone()
        if result is not None:
            searchid, generationid, individualid, genomeblob, fitnessfuncblob, status = result
            currtime = int(time.time())
            cursor.execute("BEGIN;")
            cursor.execute("UPDATE pyga SET status=%s WHERE searchid=%s AND generationid=%s AND individualid = %s and status=0;",
                (currtime, searchid, generationid, individualid))
            cursor.execute("COMMIT;")
            #print searchid, generationid, individualid
            
            genome = pickle.loads(zlib.decompress(genomeblob))
            fitnessfunc = pickle.loads(zlib.decompress(fitnessfuncblob))
            
            #this could take a while...
            fitnessfunc.generationno = generationid
            fitnessfunc.individual = individualid
            fitness = fitnessfunc(genome)
            
            fitblob = zlib.compress(pickle.dumps(fitness))
            cursor.execute("BEGIN;")
            cursor.execute("UPDATE pyga SET fitness=%s, status=-1 WHERE searchid=%s AND generationid=%s AND individualid=%s and status=%s;",
                (fitblob, searchid, generationid, individualid, currtime))
            cursor.execute("COMMIT;")
            
            #print searchid, generationid, individualid, fitness
            
        else:
            #nothing more to do
            #wait a while and see if there is still nothing
            time.sleep(1)
            cursor.execute("SELECT * FROM pyga WHERE status=0")
            result = cursor.fetchone()
            if result is None:
                #running = False
                pass
            
        
