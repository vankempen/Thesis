#!/usr/bin/python2

import time
from os import walk, path, curdir
import ujson

st = time.time()
for root, _, files in walk('data/new/'):
    if 'failed' in root:
        continue

    if len(files) > 0:  # and root[-9:-5].startswith('0506'):
        print("%s: %s" % (time.time() - st, root))
    for f in files:
        r = root[-14:]
        try:
            with open(path.join(root, f), 'r') as reader:
                a = ujson.load(reader)
            with open(path.join(root, f), 'w') as w:
                ujson.dump({'flights': a[0][0][1][3][0], 'routes': a[0][0][1][3][1]}, w)
        except ValueError:
            print("ValueError: ", root, f)
            raise ValueError
        except KeyError:
            print("KeyError: ", root, f)
            raise KeyError
print(time.time() - st)
