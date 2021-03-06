import numpy as np
import theano
import theano.tensor as T
import matplotlib.pyplot as plt

from util import getData, getBinaryData, y2indicator, error_rate, relu, init_weights_and_bias
from sklearn.utils import shuffle

class HiddenLayer(object):
    def __init__(self, M1, M2, an_id):
        self.id = an_id
        self.M1 = M1
        self.M2 = M2
        W, b = init_weights_and_bias(M1,M2)
        self.W = theano.shared(W, 'W_%s' % self.id)
        self.b = theano.shared(b, 'b_%s' % self.id)
        self.params = [self.W, self.b]

    def forward(self, X):
        return relu(X.dot(self.W)+self.b)

class ANN(object):
    def __init__(self, hidden_layer_sizes):
        self.hidden_layer_sizes = hidden_layer_sizes

    def fit(self, X , Y, learning_rate = 10e-7, mu = 0.99, decay = 0.999, epochs=400, batch_sz = 100, show_fig=False):
        X, Y = shuffle(X,Y)
        X = X.astype(np.float32)
        Y = Y.astype(np.float32)
        Xvalid, Yvalid = X[-1000:], Y[-1000:]
        X, Y = X[:-1000],Y[:-1000]

        #Initialize the hidden layers
        N, D = X.shape
        K = len(set(Y))
        self.hidden_layers = []
        M1 = D
        count = 0
        for M2 in self.hidden_layers_sizes:
            h = HiddenLayer(M1, M2, count)
            self.hidden_layers.append(h)
            M1 = M2
            count +=1

        W, b = init_weights_and_bias(M1, K)
        self.W = theano.shared(W, 'W_logreg')
        self.b = theano.shared(b, 'b_logreg')

        self.params = [self.W, self.b]
        for h in self.hidden_layers:
            self.params += h.params

        # for momemtum
        dparams = [theano.shared(np.zeros(p.get_value().shape)) for p in self.params]

        # for rmsprop
        cache = [theano.shared(np.zeros(p.get_value().shape)) for p in self.params]

        # theano vars

        thX = T.matrix('X')
        thY = T.ivector('Y')
        pY = self.forward(thX)

        rcost = reg*T.sum([(p*p).sum() for p in self.params])
        cost = -T.mean(T.log(pY[T.arange(thY.shape[0]), thY])) + rcost

        prediction = self.predict(thX)
        cost_predict_op = theano.function(
            inputs = [thX, thY],
            outputs = [cost, prediction]

        )

        updates = [
            (c, decay*x + (1-decay)*T.grad(cost, p)) for p,c in zip(self.params, cache)
        ] + [
            (p, p + mu*dp - learning_rate*T.grad(cost,p)/T.sqrt(c + 10e-10)) for p,c,dp in zip(self.params, cache, dparams)
        ] + [
            (dp, mu*dp - learning_rate*T.grad(cost,p)/T.sqrt(c + 10e-10)) for p,c,dp in zip(self.params, cache, dparams)
        ]

        train_op = theano.function(
            inputs = [thX, thY],
            updates = updates
        )

        n_batches = N / batch_sz
        costs = []
        for i in xrange(epochs):
            X, Y = shuffle(X,Y)
            for j in xrange(n_batches):
                Xbatch = X[j*batch_sz:(j*batch_sz + batch_sz)]
                Ybatch = Y[j*batch_sz:(j*batch_sz + batch_sz)]

                train_op(Xbatch, Ybatch)

                if j%20 == 0:
                    c,p = cost_predict_op(Xvalid, Yvalid)
                    costs.append(c)
                    e = error_rate(Yvalid, p)
                    print ("i:", i, "j:", j, "nb:", n_batches, "cost:", c , "error_rate:", e)

        if show_fig:
             plt.plot(costs)
             plt.show()

    def forward(self, X):
        Z = X
        for h in self.hidden_layers:
            Z = h.forward(Z)
        return T.nnet.softmax(Z.dot(self.W) + self.b)

    def predict(self,X):
        pY = self.forward(X)
        return T.argmax(pY, axis = 1)











def main():
    X, Y = getData()

    model = ANN([2000,1000])
    model.fit(X,Y, show_fig = True)

if __name__ == '__main__':
    main()