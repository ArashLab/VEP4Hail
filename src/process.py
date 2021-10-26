import argparse
import json
import os
import pickle

from Bio import bgzf

from dtypes import to_dtype, to_str, merge


def correct(obj):
    if 'colocated_variants' in obj:
        for element in obj['colocated_variants']:
            if 'frequencies' in element:
                element['frequencies'] = [{'allele': key, **value} for key, value in element['frequencies'].items()]
    return obj


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='input file path')
    parser.add_argument('corrected', help='where to store the corrected JSON')
    parser.add_argument('structure', help='where to store the structure of the JSON')
    parser.add_argument('--as-string', action='store_true', help='by default, structure is saved as a pickle')
    args = parser.parse_args()
    rest, extension = os.path.splitext(args.filepath)
    open_func = bgzf.open if extension == '.bgz' else open
    with open_func(args.filepath, 'r') as stream:
        contents = [json.loads(line) for line in stream]
    corrected = [correct(obj) for obj in contents]
    with bgzf.open(args.corrected, 'w') as stream:
        stream.write('\n'.join(json.dumps(obj) for obj in corrected))
    merged = merge([to_dtype(obj) for obj in corrected])
    if args.as_string is True:
        with open(args.structure, 'w') as stream:
            stream.write(to_str(merged))
    else:
        with open(args.structure, 'wb') as stream:
            pickle.dump(merged, stream)
