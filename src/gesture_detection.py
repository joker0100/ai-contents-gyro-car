import numpy as np
import pandas as pd
import tensorflow as tf
import modi
from gathering_data import DataGathering
import time

class DetectGesture(object):
    def __init__(self):
        self.SEED = 1337
        # the list of gestures that data is available for
        self.GESTURES = [
            #'1',
            #'2',
            #'3',
            #'4',
            #'5',
            #'9'
            'back',
            'go',
            'left',
            'right'
        ]
        self.SAMPLES_PER_GESTURE = 25


    def training_model(self):
        print(f"TensorFlow version = {tf.__version__}\n")
        # Set a fixed random seed value, for reproducibility, this will allow us to get
        # the same random numbers each time the notebook is run
        np.random.seed(self.SEED)
        tf.random.set_seed(self.SEED)
        NUM_GESTURES = len(self.GESTURES)

        # create a one-hot encoded matrix that is used in the output
        ONE_HOT_ENCODED_GESTURES = np.eye(NUM_GESTURES)

        inputs = []
        outputs = []

        # read each csv file and push an input and output
        for gesture_index in range(NUM_GESTURES):
            gesture = self.GESTURES[gesture_index]
            print(f"Processing index {gesture_index} for gesture '{gesture}'.")
            
            output = ONE_HOT_ENCODED_GESTURES[gesture_index]
            
            df = pd.read_csv("../data/" + gesture + ".csv")

            # calculate the number of gesture recordings in the file
            num_recordings = int(df.shape[0] / self.SAMPLES_PER_GESTURE)
            print(df)
            print(df.shape)
            print(f"\tThere are {num_recordings} recordings of the {gesture} gesture.")

            df = normalize(df)

            for i in range(num_recordings):
                tensor = []
                for j in range(self.SAMPLES_PER_GESTURE):
                    index = i * self.SAMPLES_PER_GESTURE + j
                    tensor += [
                        (df['aX'][index]), (df['aY'][index]), (df['aZ'][index]),
                        (df['gX'][index]), (df['gY'][index]), (df['gZ'][index]),
                        (df['roll'][index]), (df['pitch'][index]), (df['yaw'][index])
                        #(df['vi'][index])
                    ]
                    inputs.append(tensor)
                    outputs.append(output)
        
        # convert the list to numpy array
        inputs = np.array(inputs)
        outputs = np.array(outputs)
        print("Data set parsing and preparation complete.")

        # Randomize the order of the inputs, so they can be evenly distributed for training, testing, and validation
        # https://stackoverflow.com/a/37710486/2020087
        num_inputs = len(inputs)
        randomize = np.arange(num_inputs)
        np.random.shuffle(randomize)

        # Swap the consecutive indexes (0, 1, 2, etc) with the randomized indexes
        inputs = inputs[randomize]
        outputs = outputs[randomize]

        # Split the recordings (group of samples) into three sets: training, testing and validation
        TRAIN_SPLIT = int(0.6 * num_inputs)
        TEST_SPLIT = int(0.2 * num_inputs + TRAIN_SPLIT)
        print("inputs : ", len(inputs))
        print("TRAIN_SPLIT : ", TRAIN_SPLIT)
        print("TEST_SPLIT : ", TEST_SPLIT)
        print(inputs[0], outputs[0])

        inputs_train, inputs_test, inputs_validate = np.split(inputs, [TRAIN_SPLIT, TEST_SPLIT])
        outputs_train, outputs_test, outputs_validate = np.split(outputs, [TRAIN_SPLIT, TEST_SPLIT])


        print("Data set randomization and splitting complete.")
        print('inputs_train: ', len(inputs_train))
        print('inputs_train_shape: ', inputs_train.shape)
        print('inputs_test: ', len(inputs_test))
        print('inputs_validate: ', len(inputs_validate))


        # build the model and train it
        model = tf.keras.Sequential()
        # model.add(tf.keras.layers.LSTM(150, activation='relu'))
        #model.add(tf.keras.layers.Dropout(rate=.1))
        #model.add(tf.keras.layers.Dense(150, activation='relu'))
        #model.add(tf.keras.layers.Dropout(rate=.1))

        # model.add(LSTM(100, input_shape=(n_timesteps, n_features)))
        # model.add(Dropout(0.5))
        # model.add(Dense(100, activation='relu'))
        # model.add(Dense(n_outputs, activation='softmax'))
        # model.compile(loss='categorical_crossentropy', op


        #model.add(tf.keras.layers.LSTM(100, activation='relu'))
        # model.add(tf.keras.layers.Dropout(rate=.5))

        model.add(tf.keras.layers.Dense(100, activation='relu'))
        model.add(tf.keras.layers.Dropout(rate=.3))
        model.add(tf.keras.layers.Dense(50, activation='relu'))
        #model.add(tf.keras.layers.Dropout(rate=.2))
        model.add(tf.keras.layers.Dense(NUM_GESTURES, activation='softmax')) # softmax, sigmoid
        #model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['mae'])
        #model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['mae','acc']) # loss: mean_squared_error, binary_crossentropy, categorical_crossentropy
        #model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=[tf.keras.metrics.CategoricalAccuracy()])
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['acc'])
        #history = model.fit(inputs_train, outputs_train, epochs=5, batch_size=1, validation_data=(inputs_validate, outputs_validate)
        history = model.fit(inputs_train, outputs_train, epochs=5, batch_size=1)
        model.save('../model/model_car_acc_1.h5')

    def predict(self, gyro, btn):
        # bundle = modi.MODI(3)
        # self.gyro = bundle.gyros[0]
        # self.btn = bundle.buttons[0]
        # self.mot = bundle.motors[0]
        #df = DataGathering.record_motion(self, self.btn, self.gyro)
        GESTURES = [
            'back',
            'go',
            'left',
            'right'
        ]

        df = DataGathering.record_motion(self, btn, gyro)
        while df is None:
            print('retry...')
            time.sleep(1)
            df = DataGathering.record_motion(self, btn, gyro)



        model = tf.keras.models.load_model('../model/model_car_acc_1.h5')
        df = normalize(df)

        tensor = []
        inputs = []
        SAMPLES_PER_GESTURE = 25
        for j in range(SAMPLES_PER_GESTURE):
            index = j
            tensor += [
                (df['aX'][index]), (df['aY'][index]), (df['aZ'][index]),
                (df['gX'][index]), (df['gY'][index]), (df['gZ'][index]),
                (df['roll'][index]), (df['pitch'][index]), (df['yaw'][index])
                #(df['vi'][index])
            ]
        inputs.append(tensor)
        inputs = np.array(inputs)
        preds = model.predict(inputs)
        print(preds)
        print('3D Gesture Prediction = ', GESTURES[np.argmax(preds[0])])
        pred = GESTURES[np.argmax(preds[0])]
        return pred

    

def normalize(df):
    # normalize each feature of a given gesture
    df['aX'] = (df['aX'] - np.min(df['aX']))/np.ptp(df['aX'])
    df['aY'] = (df['aY'] - np.min(df['aY']))/np.ptp(df['aY'])
    df['aZ'] = (df['aZ'] - np.min(df['aZ']))/np.ptp(df['aZ'])
    df['gX'] = (df['gX'] - np.min(df['gX']))/np.ptp(df['gX'])
    df['gY'] = (df['gY'] - np.min(df['gY']))/np.ptp(df['gY'])
    df['gZ'] = (df['gZ'] - np.min(df['gZ']))/np.ptp(df['gZ'])
    df['roll'] = (df['roll'] - np.min(df['roll']))/np.ptp(df['roll'])
    df['pitch'] = (df['pitch'] - np.min(df['pitch']))/np.ptp(df['pitch'])
    df['yaw'] = (df['yaw'] - np.min(df['yaw']))/np.ptp(df['yaw'])
    df['vi'] = (df['vi'] - np.min(df['vi']))/np.ptp(df['vi'])

    return df

def main():
    dg = DetectGesture()
    dg.training_model()


if __name__ == "__main__":
    main()