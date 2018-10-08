# Imports
import pandas as pd
import numpy as np
import os, sys, inspect
from six.moves import cPickle as pickle
import scipy.misc as misc

# Parâmetros
IMAGE_SIZE = 48
NUM_LABELS = 7

# Usando 10% dos dados para validação
VALIDATION_PERCENT = 0.1  

# Normalização
IMAGE_LOCATION_NORM = IMAGE_SIZE // 2

# Seed
np.random.seed(0)

# For training 
train_error_list = []
train_step_list = []

# For validation 
valid_error_list = []
valid_step_list = []

# Emoções
emotion = {0:'anger', 
           1:'disgust',
           2:'fear',
           3:'happy',
           4:'sad',
           5:'surprise',
           6:'neutral'}

# Classe para o resultado em teste
class testResult:

    def __init__(self):
        self.anger = 0
        self.disgust = 0
        self.fear = 0
        self.happy = 0
        self.sad = 0
        self.surprise = 0
        self.neutral = 0
        
    def evaluate(self,label):        
        if (0 == label):
            self.anger = self.anger+1
        if (1 == label):
            self.disgust = self.disgust+1
        if (2 == label):
            self.fear = self.fear+1
        if (3 == label):
            self.happy = self.happy+1
        if (4 == label):
            self.sad = self.sad+1
        if (5 == label):
            self.surprise = self.surprise+1
        if (6 == label):
            self.neutral = self.neutral+1

    def display_result(self,evaluations):
        print("anger = "    + str((self.anger/float(evaluations))*100)    + "%")
        print("disgust = "  + str((self.disgust/float(evaluations))*100)  + "%")
        print("fear = "     + str((self.fear/float(evaluations))*100)     + "%")
        print("happy = "    + str((self.happy/float(evaluations))*100)    + "%")
        print("sad = "      + str((self.sad/float(evaluations))*100)      + "%")
        print("surprise = " + str((self.surprise/float(evaluations))*100) + "%")
        print("neutral = "  + str((self.neutral/float(evaluations))*100)  + "%")      


# Função para leitura dos dados
def read_data(data_dir, force=False):
    def create_onehot_label(x):
        label = np.zeros((1, NUM_LABELS), dtype=np.float32)
        label[:, int(x)] = 1
        return label

    pickle_file = os.path.join(data_dir, "EmotionDetectorData.pickle")
    if force or not os.path.exists(pickle_file):
        train_filename = os.path.join(data_dir, "train.csv")
        data_frame = pd.read_csv(train_filename)
        data_frame['Pixels'] = data_frame['Pixels'].apply(lambda x: np.fromstring(x, sep=" ") / 255.0)
        data_frame = data_frame.dropna()
        print("Lendo train.csv ...")

        train_images = np.vstack(data_frame['Pixels']).reshape(-1, IMAGE_SIZE, IMAGE_SIZE, 1)
        print(train_images.shape)
        train_labels = np.array(list(map(create_onehot_label, data_frame['Emotion'].values))).reshape(-1, NUM_LABELS)
        print(train_labels.shape)

        permutations = np.random.permutation(train_images.shape[0])
        train_images = train_images[permutations]
        train_labels = train_labels[permutations]
        validation_percent = int(train_images.shape[0] * VALIDATION_PERCENT)
        validation_images = train_images[:validation_percent]
        validation_labels = train_labels[:validation_percent]
        train_images = train_images[validation_percent:]
        train_labels = train_labels[validation_percent:]

        print("Lendo test.csv ...")
        test_filename = os.path.join(data_dir, "test.csv")
        data_frame = pd.read_csv(test_filename)
        data_frame['Pixels'] = data_frame['Pixels'].apply(lambda x: np.fromstring(x, sep=" ") / 255.0)
        data_frame = data_frame.dropna()
        test_images = np.vstack(data_frame['Pixels']).reshape(-1, IMAGE_SIZE, IMAGE_SIZE, 1)

        with open(pickle_file, "wb") as file:
            try:
                print('\nSalvando ...')
                save = {
                    "train_images": train_images,
                    "train_labels": train_labels,
                    "validation_images": validation_images,
                    "validation_labels": validation_labels,
                    "test_images": test_images,
                }
                pickle.dump(save, file, pickle.HIGHEST_PROTOCOL)

            except:
                print("Não foi possível salvar :/")

    with open(pickle_file, "rb") as file:
        save = pickle.load(file)
        train_images = save["train_images"]
        train_labels = save["train_labels"]
        validation_images = save["validation_images"]
        validation_labels = save["validation_labels"]
        test_images = save["test_images"]

    return train_images, train_labels, validation_images, validation_labels, test_images
