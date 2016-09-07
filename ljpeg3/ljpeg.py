import os
import subprocess
import re
from glob import glob
import numpy as np


def ics_file_name(path):
    dir_name = os.path.dirname(path)
    ics_files = glob(dir_name + '/*.ics')
    if len(ics_files) == 0:
        print('found no corresponding ics file')
        return None
    elif len(ics_files) == 1:
        print('found ics file')
        return ics_files[0]
    else:
        print('found multiple ics files! Using first one.')
        return ics_files[0]


def ljpeg_file_name_base(path):
    return path.split('.')[-2]


def read_ics(ics_file, ljpeg_file):
    print(ics_file)
    for l in open(ics_file, 'r'):
        l = l.strip().split(' ')
        if len(l) < 7:
            continue
        if l[0] == ljpeg_file:
            W = int(l[4])
            H = int(l[2])
            bpp = int(l[6])
            if bpp != 12:
                print('BPP != 12: {} in {}'.format(bpp, ics_file))  # this probably doesn't matter
            return W, H, bpp


def read(ljpeg_path):
    # Check for the compiled ljpeg binary
    pkg_dir = os.path.dirname(__file__)
    pkg_root, _ = os.path.split(pkg_dir)
    BIN = os.path.join(pkg_root, "jpegdir", "jpeg")
    if not os.path.exists(BIN):
        raise FileNotFoundError('jpeg is not built yet; use \'cd jpegdir; make\' first')

    # Compose and execute the command
    cmd = '{} -d -s {}'.format(BIN, ljpeg_path)
    l = subprocess.check_output(cmd, shell=True)

    # Fetch some information from the beginning of the output
    pattern = re.compile(b'\sC:(\d+)\s+N:(\S+)\s+W:(\d+)\s+H:(\d+)\s')
    m = re.search(pattern, l)
    ljpeg_out = {'c': int(m.group(1)),  # aaalgo: I suppose this is # channels (https://github.com/aaalgo/ljpeg)
                 'f': m.group(2),  # This seems to be the output file
                 'w': int(m.group(3)),  # Most likely width, often wrong, check ics file instead
                 'h': int(m.group(4))}  # Height, see above

    if not ljpeg_out['c'] == 1:
        raise Exception('C != 1, could there be more than 1 channel in the image?')

    # Set width and height
    cmd_w = ljpeg_out['w']
    cmd_h = ljpeg_out['h']

    w = cmd_w
    h = cmd_w

    # Search for ics file and load data from it. Prefer data from this file if available
    ics_file = ics_file_name(ljpeg_path)
    if ics_file:
        ics_w, ics_h, ics_bps = read_ics(ics_file, ljpeg_file_name_base(ljpeg_path))

        if (ics_w * ics_h) != (cmd_w * cmd_h):
            # shape is not identical, prefer subprocess output
            pass
        else:
            # prefer width and height from ics if given
            w = ics_w
            h = ics_h

    # Load the image from the output file
    im = np.fromfile(ljpeg_out['f'], dtype='uint16').reshape(h, w)

    # Nice! We've got some bit shifting voodoo!
    # I have no idea what is going on here
    # Update: I do. It's converting from little to big endian. Nice!
    # Basically swapping two 8-pairs of bits in an 16-bit integer.
    L = im >> 8  # shift bits of im right by 8 bits
    H = im & 0xFF  # masking: selecting only the last 8 bits of im
    im = (H << 8) | L  # shift the other bits 8 positions to the left and "join" with L

    # Remove the output file
    os.remove(ljpeg_out['f'])

    return im
