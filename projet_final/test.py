from player import Player
from config import *
import numpy as np

import matplotlib.pyplot as plt


for strength in [1, 3, 6, 10]:
    vs = np.random.lognormal(np.log(strength + 5), 2/(strength + 5), 10000) - 5

    plt.hist(vs, bins=100, density=True, alpha=0.6, label=f'Strength {strength}')

plt.xlim(0, 25)
plt.legend()
plt.show()
