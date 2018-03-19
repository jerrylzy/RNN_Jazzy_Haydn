'''
Author:     Ji-Sung Kim
Project:    deepjazz
Purpose:    Parse, cleanup and process data.

Code adapted from Evan Chow's jazzml, https://github.com/evancchow/jazzml with
express permission.
'''

from __future__ import print_function

from music21 import *
from collections import defaultdict, OrderedDict
from itertools import groupby, zip_longest

from grammar import *

from grammar import parse_melody
from music_utils import *

#----------------------------HELPER FUNCTIONS----------------------------------#

''' Helper function to parse a MIDI file into its measures and chords '''
def __parse_midi(data_fn):
    # Parse the MIDI data for separate melody and accompaniment parts.
    midi_data = converter.parse(data_fn)

    # Get melody part, compress into single voice.
    melody_stream = midi_data[0]     # For the Hadyn piano piece, Melody is Part #0.
    melody1, melody2 = melody_stream.getElementsByClass(stream.Voice)
    for j in melody2:
        melody1.insert(j.offset, j)
    melody_voice = melody1

    for i in melody_voice:
        if i.quarterLength == 0.0:
            i.quarterLength = 0.25

    # Use its original keys
    melody_voice.insert(0, instrument.Piano())
    melody_voice.insert(0, key.Key('C'))
    melody_voice.insert(0, key.Key('E-'))
    melody_voice.insert(0, key.Key('E-'))
    melody_voice.insert(0, key.Key('C'))

    # Add all accompany parts
    partIndices = [1, 2, 3]
    comp_stream = stream.Voice()
    comp_stream.append([j.flat for i, j in enumerate(midi_data) 
        if i in partIndices])

    # Full stream containing both the melody and the accompaniment. 
    # All parts are flattened. 
    full_stream = stream.Voice()
    for i in range(len(comp_stream)):
        full_stream.append(comp_stream[i])
    full_stream.append(melody_voice)

    # Extract solo stream, assuming you know the positions ..ByOffset(i, j).
    # Note that for different instruments (with stream.flat), you NEED to use
    # stream.Part(), not stream.Voice().
    # While 200 is an arbitrary lower bound, 480 is the highest frequency in the piece.
    solo_stream = stream.Voice()
    for part in full_stream:
        curr_part = stream.Part()
        curr_part.append(part.getElementsByClass(instrument.Instrument))
        curr_part.append(part.getElementsByClass(tempo.MetronomeMark))
        curr_part.append(part.getElementsByClass(key.KeySignature))
        curr_part.append(part.getElementsByClass(meter.TimeSignature))
        curr_part.append(part.getElementsByOffset(200, 480, 
                                                  includeEndBoundary=True))
        cp = curr_part.flat
        solo_stream.insert(cp)

    # Group by measure so you can classify. 
    # Note that measure 0 is for the time signature, metronome, etc. which have
    # an offset of 0.0.
    melody_stream = solo_stream[-1]
    measures = OrderedDict()
    offsetTuples = [(int(n.offset / 4), n) for n in melody_stream]
    
    # Need to make the following changes to avoid 0 chords in an array
    '''
    2 (0, <music21.meter.TimeSignature 3/4>)

    34 (180, <music21.key.Key of E- major>) remove~!!
    35 (180, <music21.key.Key of E- major>)
    36 (186, <music21.key.Key of E- major>)
    37 (186, <music21.key.Key of E- major>)

    38 (199<music21.key.Key of C major>)
    39 (199music21.key.Key of C major>)
    '''
    offsetTuples[2] = (0, offsetTuples[2][1])
    offsetTuples[38] = (199, offsetTuples[38][1])
    offsetTuples[39] = (199, offsetTuples[39][1])
    del offsetTuples[36]
    del offsetTuples[34]
    
    measureNum = 0 # for now, don't use real m. nums (119, 120)
    for key_x, group in groupby(offsetTuples, lambda x: x[0]):
        measures[measureNum] = [n[1] for n in group]
        measureNum += 1

    # Get the stream of chords.
    # offsetTuples_chords: group chords by measure number.
    chordStream = solo_stream[1]
    chordStream.removeByClass(note.Rest)
    chordStream.removeByClass(note.Note)
    offsetTuples_chords = [(int(n.offset / 4), n) for n in chordStream]
    
    # Need to make the following changes to avoid 0 chords in an array
    '''
    2 (0, <music21.meter.TimeSignature 3/4>)
    29 (183, <music21.key.Key of E- major>)
    30 (183, <music21.key.Key of E- major>)
    34 (189, <music21.key.Key of E- major>)
    35 (189, <music21.key.Key of E- major>)
    '''
    offsetTuples_chords[2] = (0, offsetTuples[2][1])
    offsetTuples_chords[29] = (183, offsetTuples[29][1])
    offsetTuples_chords[30] = (183, offsetTuples[30][1])
    offsetTuples_chords[34] = (189, offsetTuples[34][1])
    offsetTuples_chords[35] = (189, offsetTuples[35][1])

    # Generate the chord structure. Use just track 1 (piano) since it is
    # the only instrument that has chords. 
    # Group into 4s, just like before. 
    chords = OrderedDict()
    measureNum = 0
    for key_x, group in groupby(offsetTuples_chords, lambda x: x[0]):
        chords[measureNum] = [n[1] for n in group]
        measureNum += 1

    # Trim the measures to have an equal length with chords.
    for i in range(len(measures) - len(chords)):
        del measures[len(measures) - 1]
    assert len(chords) == len(measures)

    return measures, chords

''' Helper function to get the grammatical data from given musical data. '''
def __get_abstract_grammars(measures, chords):
    # extract grammars
    abstract_grammars = []
    for ix in range(0, len(measures) - 1):
        m = stream.Voice()

        # Avoid repetitions that results in an insersion error
        testSet = set()
        for i in measures[ix]:
            testStr = str(i.offset) + str(i)
            if testStr in testSet:
                continue
            m.insert(i.offset, i)
            testSet.add(testStr)
            
        c = stream.Voice()
        testSet = set()
        for j in chords[ix]:
            testStr = str(j.offset) + str(j)
            if testStr in testSet:
                continue
            c.insert(j.offset, j)
            testSet.add(testStr)
            
        parsed = parse_melody(m, c)

        # Ignore zero-length measure / chords
        if parsed != None:
            abstract_grammars.append(parsed)

    return abstract_grammars

#----------------------------PUBLIC FUNCTIONS----------------------------------#

''' Get musical data from a MIDI file '''
def get_musical_data(data_fn):
    
    measures, chords = __parse_midi(data_fn)
    abstract_grammars = __get_abstract_grammars(measures, chords)

    return chords, abstract_grammars

''' Get corpus data from grammatical data '''
def get_corpus_data(abstract_grammars):
    corpus = [x for sublist in abstract_grammars for x in sublist.split(' ')]
    values = set(corpus)
    val_indices = dict((v, i) for i, v in enumerate(values))
    indices_val = dict((i, v) for i, v in enumerate(values))

    return corpus, values, val_indices, indices_val

'''
def load_music_utils():
    chord_data, raw_music_data = get_musical_data('data/original_metheny.mid')
    music_data, values, values_indices, indices_values = get_corpus_data(raw_music_data)

    X, Y = data_processing(music_data, values_indices, Tx = 20, step = 3)
    return (X, Y)
'''
