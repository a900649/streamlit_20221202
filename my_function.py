import pickle
import os

def save_obj(obj, name ):

    a = os.path.dirname(os.path.abspath(__file__))

    with open(a + "\\" + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    a = os.path.dirname(os.path.abspath(__file__))

    if ".pkl" in name :
        name = name
    else :
        name = name + '.pkl'
    with open(a + "\\" +name , 'rb') as f:
        return pickle.load(f)