# Velázquez Lab Code
Code for Jessica (and Velázquez Lab).

> Michael Poehlmann

> poehlmann@ucdavis.edu

To download this repository, run
```bash
git clone git@github.com:mpoehlmann/velazquez_lab.git
```

## Running instructions
If this is your first time running the code, please first go though the ``tutorials/computing_environment.md`` tutorial on how to setup your computer.

Before running the code, you need to activate your conda environment and setup the Python package.
From this project directory, run:
```bash
setup_conda
python setup.py develop
```

## Project structure
``./``
├── ``environment.yml``: file used to create ``conda`` computing environment
├── ``README.txt``: important project information and instructions
├── ``scripts/``: scripts to run various types of analyses
├── ``tutorials/``: a collection of useful tutorials on topics including Python, coding, curve-fitting, and error propagation
│   └── ``computing_environment.md``: instructions for setting up your computing environment
└── ``velazquez_lab/``: folder containing all Python modules
    ├── ``eis/``: electrochemical impedance spectroscopy tools
    ├── ``gc/``: gas chromatography tools
    ├── ``nmr/``: nuclear magnetic resonance tools
    ├── ``pol/``: polarization curve tools
    │   ├── ``julius/``: newly implemented Tafel slope method
    │   └── ``legacy/``: code used for previous calculations of Tafel slope
    └── ``utils/``: utilities used throughout project


## TODO
- eis
  - eis --> look for circuit fit

- ecsa
  - cv
- polarization_curves:
  - lsv

- gc
  - input actual --> set
  - input set --> actual
  - list of inputs --> create full spreadsheets
  - do rest of math to get current (mimic spreadsheet)

- external
  - julius (polarization: tafel slope)
  - fuelcell (eis)

- jupyter
  - https://blog.jupyter.org/and-voilà-f6a2c08a4a93
- excel
  - https://www.youtube.com/watch?v=uFJ8wpgoq_E