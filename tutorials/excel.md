# Microsoft Excel integration with Python
For Windows computers, Excel can run Python scripts by using the [xlwings](https://www.xlwings.org) package.
Here are instructions.

## Setup instructions
Open the Anaconda prompt.
In ``velazquez_lab`` folder (not the inner one), run
```bash
conda activate labenv
python setup.py develop
```

Edit ``C:/Users/Jessica/.xlwings/xlwings`` (replace ``Jessica`` with your username) and add the module to be imported.
Separate modules with semi-colon and no space.
For example,

FIXME:
In Excel, open up the Developer console (Alt-F11) Click on Tools -> References and select xlwings

Now, to call a function, edit a cell and type ``=python_func_name(cells)`` followed by ``Ctrl+Enter``.