import tomllib
import numpy as np

def toml_numpify(config):
    out = {}
    for sec,dic in config.items():
        if 'numpy' in dic:
            out[sec] = {k: (np.array(v) if k in dic['numpy'] else v) 
                        for k,v in dic.items() if k != 'numpy'}    
        else:
            out[sec] = dic

    return out

def load_numpified_toml(filename):
    with open(filename,'rb') as f:
        return toml_numpify(tomllib.load(f))