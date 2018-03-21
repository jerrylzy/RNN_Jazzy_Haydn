# RNN Jazzy Hadyn
This is an LSTM-based Recurrent Neural Network trained on Piano Sonata No. 48 III Finale. 

The training file can be found at [kunstderfuge.com](http://www.kunstderfuge.com/haydn.htm).

* All preprocessing files are modified from Ji-Sung Kim's work [deepjazz](https://github.com/jisungk/deepjazz).
* The model is from [Coursera](https://www.coursera.org/learn/nlp-sequence-models/notebook/cxJXc/jazz-improvisation-with-lstm).

This is more of an exploration rather than a serious project.

### Environment Setup

1. Download and install [Anaconda](https://www.anaconda.com/download/)

2. Create and activate environment

    ```shell
    conda update -n base conda
    conda create --name ml numpy scipy h5py jupyter keras
    source activate ml
    pip install --upgrade pip
    pip install music21 matplotlib
    ```

3. [Install Tensorflow](https://www.tensorflow.org/install). For example

    ```shell
    pip install --ignore-installed --upgrade https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-1.6.0-py3-none-any.whl
    ```

4. Launch the Jupyter Notebook

    ```shell
    jupyter notebook
    ```

5. Run the notebook `Jazzy Haydn.ipynb`

6. Get the result from `output/my_music.midi`

### Data Preprocessing
Most code is adopted from Ji-Sung Kim's work which is based on Evan Chow's [jazzml](https://github.com/evancchow/jazzml). 
However, some parts are tailored specifically for his training data.

* `data_utils.py`: moved function `generate_music` to the jupyter notebook. Use variable `N_tones` for `num_classes` everywhere.
* `grammar.py`: return `None` if either the list `measure` or `chords` has a length 0.
* `inference_code.py`: Use the same `N_tones` as the one in `data_utils.py`.
* `music_utils.py`: moved the `one_hot` helper function to the jupyter notebook.
* `preprocess.py`: Multiple changes to the `__parse_midi` function to make it compatible with our training data.

### Model
We adopted the model from Coursera. It is a one-to-many LSTM RNN with 64 memory cells. It uses the output of the previous cell as the input of the current cell.

We train this model with 100 epoches, and generate 50 new values from the network.
