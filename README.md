# ljpeg3

### Open ljpeg files as NumPy arrays

This is a wrapper around the Stanford ljpeg code, which is public domain and also included.
It's loosely based on [@aaalgo/ljpeg], updated for Python 3 and slightly refactored.

You probably would want to use it to open images from the [DDSM] Mammography Database, as they had the genius idea of using this near-extinct image format.

## Installation

You should have NumPy installed:
```shell
pip3 install numpy
```

Clone this repository:

```shell
git clone https://github.com/olieidel/ljpeg3.git
```

Build the ljpeg stuff. Some warnings may appear, ignore them and hope for the best. I have no idea how to fix the C code if it doesn't work for you.

```shell
cd ljpeg3/jpegdir
make
```

## Usage

In your python project, add ljpeg3 to your path and import it:

```python
import sys
sys.path.append('/path_to/ljpeg3')
from ljpeg3 import ljpeg
```

Read a .ljpeg file. There should also be an .ics file in the same directory.

```python
im = ljpeg.read('path_to/some_file.ljpeg')
```

Use NumPy for further processing. Good luck!

## Notes

In most cases, the height and width information from the ljpeg file is swapped and the ics file is needed to correct it. Oh, and swapped height und width is not equivalent to simply transposing the matrix.. :)

If you don't have an .ics file and your image looks weird, try this:

```python
im = ljpeg.read('path_to/some_file.ljpeg')
im.reshape((im.shape[1], im.shape[0]))  # swaps width and height

# im.T <-- this won't work
```

<!-- Links -->
[@aaalgo/ljpeg]: https://github.com/aaalgo/ljpeg
[DDSM]: http://marathon.csee.usf.edu/Mammography/Database.html