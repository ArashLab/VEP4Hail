import json

primitive_types = {
    str: 'str',
    int: 'int32',
    float: 'float32',
}

dtypes_generalization = {
    'int32': -1,
    'float32': -2,  # Can hold an integer without data loss.
    'str': -3,  # Can hold an integer or a decimal number without data loss.
}


def to_dtype(obj):
    if isinstance(obj, dict):
        return {key: to_dtype(value) for key, value in obj.items() if value is not None}
    if isinstance(obj, list):
        return [to_dtype(value) for value in obj]
    try:
        return primitive_types[type(obj)]
    except KeyError:
        raise RuntimeError(f'Unknown primitive type: {type(obj)}.')


def merge(dtypes):
    if isinstance(dtypes, dict):
        return {key: merge(value) for key, value in dtypes.items()}
    if isinstance(dtypes, list):
        if not dtypes:  # Empty
            return None
        if all(isinstance(element, dict) for element in dtypes):
            # Assuming the same keys have the same data types in all the dictionaries in the list.
            merged = {}
            for di in dtypes:
                merged.update(merge(di))
            return [merged]
        if all(any(isinstance(element, t) for t in primitive_types) for element in dtypes):
            most_general_dtype, *rest = sorted(dtypes, key=dtypes_generalization.get)
            return [most_general_dtype]
        raise RuntimeError(f'Undefined, how to merge {dtypes}?')
    if dtypes in primitive_types.values():
        return dtypes
    else:
        raise RuntimeError(f'Unknown input to merge func: {dtypes}.')


def to_str(dtypes):
    naive = json.dumps(dtypes, indent=2)
    return naive.replace('{', 'struct {').replace('[', 'array <').replace(']', '>').replace('"', '')
