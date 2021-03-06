import numpy as np
import matplotlib.pyplot as plt

from util import getData

label_map = ['Anger','Disgust','Fear','Happy','Sad', 'Surprised','Neutral']

def main ():
    X, Y = getData(balance_ones=False)

    while True:
        for i in xrange(7):
            x,y = X[Y==i], Y[Y==i]
            N = len(Y)
            j = np.random.choice(N)
            plt.imshow(x[j].reshape(48,48),cmap = 'gray')
            plt.title(label_map[y[j]])
            plt.show()
        prompt = raw_input('Quit? Enter Y:\n')
        if prompt == 'Y':
            break

if __name__ == '__main__':
    main()