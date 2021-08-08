# -*- coding: utf-8 -*-
"""Sentiment Analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1sy9c5UUSPwiy4DMcV3EZXTjDVwhTZ147
"""

import tensorflow as tf
from tensorflow.keras import Sequential, layers, Model, Input, optimizers
import numpy as np
from matplotlib import pyplot as plt
from nltk.tokenize import RegexpTokenizer
from tqdm import tqdm

!wget http://nlp.stanford.edu/data/glove.6B.zip
!unzip -q glove.6B.zip

EMBEDDING_DIM = 300
OUTPUT_DIM = 5

TRAIN_X = []
TEST_X = []
TRAIN_Y = []
TEST_Y = []
VALID_X = []
VALID_Y = []

MAPPINGS = [line.split()[1] for line in open('').readlines() if line != '']

DICTIONARY = {}
def prepare_embeddings(filepath):
    with open(filepath) as f:
        for line in f:
            word, coefs = line.split(maxsplit=1)
            coefs = np.fromstring(coefs, "f", sep=" ")
            DICTIONARY[word] = coefs

'''helper functions'''

#displays time as h:mm:ss
def format_time(seconds):
    return "{}:{:0>2}:{:0>2}".format(int(seconds//3600), int((seconds//60)%60), int(seconds%60))

#tokenizes and vectorizes dataset
def prepare_dataset():
    tokenizer = RegexpTokenizer(r'\w+')
    TRAIN_X = [[DICTIONARY.get(word.lower(), np.zeros(EMBEDDING_DIM)) for word in tokenizer.tokenize(line)] for line in open('').readlines() if line != '']
    TRAIN_Y = [int(line) for line in open('').readlines() if line != '']
    for i in len(TRAIN_Y):
        arr = np.zeros((OUTPUT_DIM))
        arr[TRAIN_Y[i]] = 1
        TRAIN_Y[i] = arr

    TEST_X = [[DICTIONARY.get(word.lower(), np.zeros(EMBEDDING_DIM)) for word in tokenizer.tokenize(line)] for line in open('').readlines() if line != '']
    TEST_Y = [int(line) for line in open('').readlines() if line != '']
    for i in len(TEST_Y):
        arr = np.zeros((OUTPUT_DIM))
        arr[TEST_Y[i]] = 1
        TEST_Y[i] = arr

    VALID_X = [[DICTIONARY.get(word.lower(), np.zeros(EMBEDDING_DIM)) for word in tokenizer.tokenize(line)] for line in open('').readlines() if line != '']
    VALID_Y = [int(line) for line in open('').readlines() if line != '']
    for i in len(VALID_Y):
        arr = np.zeros((OUTPUT_DIM))
        arr[VALID_Y[i]] = 1
        VALID_Y[i] = arr

#loads a batch from the dataset into memory
def get_batch(batch_size, set='train'):
    if set == 'train':
        indices = np.random.randint(TRAIN_X.shape[0], size=batch_size)
        return np.array(TRAIN_X[indices]), np.array(TRAIN_Y[indices])
    elif set == 'test':
        indices = np.random.randint(TRAIN_X.shape[0], size=batch_size)
        return np.array(TEST_X[indices]), np.array(TEST_Y[indices])
    elif set == 'valid':
        indices = np.random.randint(TRAIN_X.shape[0], size=batch_size)
        return np.array(VALID_X[indices]), np.array(VALID_Y[indices])

def build_model(num_outputs, rnn_units):
    return Sequential([
        LSTM(rnn_units, return_sequences=True),
        Dropout(0.5),
        LSTM(rnn_units, return_sequences=False),
        Dropout(0.5),
        Dense(num_outputs, activation='softmax')
    ])

@tf.function
def train_step(model, x, y):
    with tf.GradientTape() as tape:
        y_hat = model(x)
        loss = losses.categorical_crossentropy(y, y_hat)

    grads = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(grads, model.trainable_variables))
    return loss

def train():
    loss_history = []
    prev_time = time.time()
    time_elapsed = 0
    for iteration in range(iterations):
        #grab a batch and propagate it through the network
        x_batch, y_batch = get_batch(seq_length, batch_size)
        loss = train_step(x_batch, y_batch)

        #update the loss history
        loss_history.append(loss.numpy().mean())

        #update the model with the changed weights after every 100 iterations
        if iteration % 100 == 0:
            model.save_weights(checkpoint_prefix)

        time_elapsed += time.time() - prev_time
        prev_time = time.time()
        print("iteration {} of {}. Loss: {}. Time elapsed: {} seconds.".format(iteration+1, iterations, loss.numpy().mean(), time_elapsed))

    # Save the trained model and the weights
    model.save_weights(checkpoint_prefix)

    #plot a graph that will show how our loss varied with time
    plt.plot(range(iterations), loss_history)
    plt.title(__file__)
    plt.xlabel("iterations")
    plt.ylabel("Loss")
    plt.show()