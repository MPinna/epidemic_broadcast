import pandas
import numpy as np 
import pylab 
import scipy.stats as stats
from matplotlib import pyplot as plt
def lorenz_curve(X):
    X_lorenz = X.cumsum() / X.sum()
    X_lorenz = np.insert(X_lorenz, 0, 0) 
    X_lorenz[0], X_lorenz[-1]
    fig, ax = plt.subplots(figsize=[6,6])
    ## scatter plot of Lorenz curve
    ax.scatter(np.arange(X_lorenz.size)/(X_lorenz.size-1), X_lorenz, 
               marker='.', color='darkgreen', s=100)
    ## line plot of equality
    ax.plot([0,1], [0,1], color='k')

measurements = np.random.normal(loc = 20, scale = 5, size=100)   
#stats.probplot(measurements, dist="exp", plot=pylab)
g1=plt.subplot()
unif=np.random.uniform(0,100,100)
g1.scatter([0:100],unif, marker='.', color='darkgreen', s=100)
#pylab.show()

X = np.append(np.random.poisson(lam=10, size=40), 
              np.random.poisson(lam=100, size=10))
Y=np.append(np.random.uniform(100,1,100),0)
lorenz_curve(Y)
plt.show()