from molepro.transformers import * 
from molepro.server import elements
from molepro.server import set_base_url
import molepro.save as save
import sys
import csv

with open(sys.argv[1]) as csvfile:
    reader = csv.reader(csvfile, delimiter='\t', quotechar='"')
    for row in reader:
        name = row[2]
        curie = ''
        if name != '':
            print(name)
            molepro = compound_producer(name)
            for e in elements(molepro):
                print(name,e.id,sep='\t')
                if curie == '':
                    curie = e.id
        print('output', name, curie, sep='\t')
