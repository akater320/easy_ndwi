import gzip
import sys

fileName = sys.argv[1]
if not fileName:
    fileName="index.csv.gz"

with gzip.open(sys.argv[1], 'rt') as f:
    for i in range(5): 
        line = f.readline()
        print(line)
