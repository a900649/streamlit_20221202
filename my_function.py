import pickle

def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    if ".pkl" in name :
        name = name
    else :
        name = name + '.pkl'
    with open(name , 'rb') as f:
        return pickle.load(f)