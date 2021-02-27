import os
import threading as th
import sys

#print all pki plots, multithread run
os.system("python3.8 python/plots.py 'duration (s)' mean &")
os.system("python3.8 python/plots.py 'duration (s)' median &")
os.system("python3.8 python/plots.py 'collisions' mean &")
os.system("python3.8 python/plots.py 'collisions' median &")
os.system("python3.8 python/plots.py 'coverage (%)' mean &")
os.system("python3.8 python/plots.py 'coverage (%)' median")