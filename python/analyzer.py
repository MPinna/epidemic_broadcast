import subprocess

#print all pki plots, multithread run
subprocess.Popen(["python", "plots.py", 'duration (s)' ,"median" ,"0.95"])
subprocess.Popen(["python", "plots.py", 'duration (s)' ,"mean" ,"0.95"])
subprocess.Popen(["python", "plots.py", 'collisions' ,"median" ,"0.95"])
subprocess.Popen(["python", "plots.py", 'collisions' ,"mean" ,"0.95"])
subprocess.Popen(["python", "plots.py", 'coverage (%)' ,"median" ,"0.95"])
subprocess.Popen(["python", "plots.py", 'coverage (%)' ,"mean" ,"0.95"])