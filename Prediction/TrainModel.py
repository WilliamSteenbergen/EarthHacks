import tensorflow as tf
import numpy as np
import pandas as pd
from tensorflow.keras import datasets, layers, models
import matplotlib.pyplot as plt


labels = np.genfromtxt('/Users/williamsteenbergen/PycharmProjects/EarthHacks/Prediction/labels.csv', delimiter=',')
images = np.load('/Users/williamsteenbergen/PycharmProjects/EarthHacks/Prediction/images.npz')

dataset = np.zeros((len(images), 50, 50, 4))

for i in range(0,len(images)):
	dataset[i,:,:,:] = images['arr_' + str(i)]

#normalize pixel values
dataset = dataset/255
# dataset = np.random.shuffle(dataset)

train_images = dataset[0:350,:,:,:]
test_images = dataset[351:405,:,:,:]
train_labels = labels[0:350]
test_labels = labels[351:450]

def create_model():

	model = models.Sequential()
	model.add(layers.Conv2D(50, (4, 4), activation='relu', input_shape=(50, 50, 4)))
	model.add(layers.MaxPooling2D((2, 2)))
	model.add(layers.Conv2D(50, (4, 4), activation='relu'))
	model.add(layers.MaxPooling2D((2, 2)))
	model.add(layers.Conv2D(50, (4, 4), activation='relu'))
	model.add(layers.Flatten())
	model.add(layers.Dense(50, activation='relu'))
	model.add(layers.Dense(1))

	model.compile(optimizer='adam',
	              loss=tf.keras.losses.MeanSquaredError(),
	              metrics=[tf.keras.metrics.RootMeanSquaredError()])

	return model

model = create_model()

model.fit(train_images, train_labels, epochs=10,
                    validation_data=(test_images, test_labels))
model.save('saved_model/Model1')