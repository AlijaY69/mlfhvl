from tensorflow import keras
import numpy as np
from matplotlib import pyplot as plt

(x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data() 


x_train = np.reshape(x_train, (60000, 784))

x_test = np.reshape(x_test, (10000, 784))

x_train = x_train / 255
x_test = x_test / 255

y_train = keras.utils.to_categorical(y_train, 10)
y_test = keras.utils.to_categorical(y_test, 10)

model = keras.Sequential() 
model.add(keras.layers.Dense(256, activation='relu', input_shape=(784,))) 
model.add(keras.layers.Dense(10, activation='softmax'))

model.compile(loss='categorical_crossentropy', 
optimizer=keras.optimizers.RMSprop(), metrics=['accuracy']) 

history = model.fit(x_train, y_train, batch_size=128, epochs=12, verbose=1, validation_split=0.2) 


plt.plot(history.history['accuracy'], label='accuracy')
plt.plot(history.history['val_accuracy'], label='val_accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(loc='lower right')
plt.show()

plt.plot(history.history['loss'], label = 'loss')
plt.plot(history.history['val_loss'], label = 'val_loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(loc= 'upper right')
plt.show()

loss, accuracy = model.evaluate(x_test, y_test, verbose=0) 

print(f"Test accuracy: {accuracy}")
print(f"Test loss: {loss}")