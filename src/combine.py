import argparse
import fnmatch
import os
import pickle

from dtypes import merge, to_str


def load_pickle(filepath):
    with open(filepath, 'rb') as stream:
        return pickle.load(stream)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filepaths', help='input files paths as a wildcard')
    parser.add_argument('save_to', help='where to save the merged structure')
    parser.add_argument('--as-pickle', help='by default, structure is saved as a string')
    args = parser.parse_args()
    dirpath, pattern = os.path.split(args.filepaths)
    matching = [filename for filename in os.listdir(dirpath) if fnmatch.fnmatch(filename, pattern)]
    structures = [load_pickle(os.path.join(dirpath, filename)) for filename in matching]
    merged = merge(structures, singleton=True)
    if args.as_pickle is True:
        with open(args.save_to, 'wb') as stream:
            pickle.dump(merged, stream)
    else:
        with open(args.save_to, 'w') as stream:
            stream.write(to_str(merged))

