from music_utils import * 
from preprocess import * 
from keras.utils import to_categorical

chords, abstract_grammars = get_musical_data('sonata_48_3_(c)iscenko.mid')
corpus, tones, tones_indices, indices_tones = get_corpus_data(abstract_grammars)
N_tones = len(set(corpus))
n_a = 64
x_initializer = np.zeros((1, 1, N_tones))
a_initializer = np.zeros((1, n_a))
c_initializer = np.zeros((1, n_a))

def load_music_utils():
    chords, abstract_grammars = get_musical_data('sonata_48_3_(c)iscenko.mid')
    corpus, tones, tones_indices, indices_tones = get_corpus_data(abstract_grammars)
    N_tones = len(set(corpus))
    X, Y, N_tones = data_processing(corpus, tones_indices, 60, 30)   
    return (X, Y, N_tones, indices_tones)


def predict_and_sample(inference_model, x_initializer = x_initializer, a_initializer = a_initializer, 
                       c_initializer = c_initializer):
    """
    Predicts the next value of values using the inference model.
    
    Arguments:
    inference_model -- Keras model instance for inference time
    x_initializer -- numpy array of shape (1, 1, 78), one-hot vector initializing the values generation
    a_initializer -- numpy array of shape (1, n_a), initializing the hidden state of the LSTM_cell
    c_initializer -- numpy array of shape (1, n_a), initializing the cell state of the LSTM_cel
    Ty -- length of the sequence you'd like to generate.
    
    Returns:
    results -- numpy-array of shape (Ty, 78), matrix of one-hot vectors representing the values generated
    indices -- numpy-array of shape (Ty, 1), matrix of indices representing the values generated
    """
    
    ### START CODE HERE ###
    pred = inference_model.predict([x_initializer, a_initializer, c_initializer])
    indices = np.argmax(pred, axis = -1)
    results = to_categorical(indices, num_classes=N_tones)
    ### END CODE HERE ###
    
    return results, indices
