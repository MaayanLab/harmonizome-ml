import os

for root, dirs, files in os.walk('.'):
    for f in files:
    	os.rename(f, f.replace('.PNG', '.png'))
