# idl2py
Converts (some) IDL to Python

Use the .bat on Windows to drop **IDL** `.pro` files to be converted to **Python** `.py` files.

Or enter the fileName after the except: near the bottom of the file and run the `idl2py.py` file directly.

You can provide **IDL** libaries your `.pro` files call in a folder called `libs`. There is no order needed inside the folder `libs` except for your sanity.

The outputs will be put in the folder that `idl2py.py` is run from in a folder called `converted`. There may be a folder in `converted` called `pylibs` that hold converted IDL functions, you'll need those too. The converted code calls them relatively.

In this current state `idl2py` is designed to help you get started with a conversion, especially for large projects. Ideally `idl2py` will at least correctly take care of basic syntax conversion.
