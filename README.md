# Velázquez Lab Code

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/mpoehlmann/velazquez_lab/main?filepath=app.ipynb)

Code to make Jessica's life easier (and for the Velázquez Lab).

> Michael Poehlmann<br>
> poehlmann@ucdavis.edu

To download this repository, run
```bash
git clone git@github.com:mpoehlmann/velazquez_lab.git
```

## Setup instructions

If this is your first time running the code, please first go though the ``tutorials/computing_environment.md`` tutorial on how to setup your computer.

Before running the code, you need to activate your conda environment and setup the Python package.
From this project directory, run:

```bash
setup_conda
python setup.py develop
```

## Project structure

```
./
├── environment.yml: file used to create conda computing environment
├── README.txt: important project information and instructions
├── scripts/: scripts to run various types of analyses
├── tutorials/: a collection of useful tutorials on topics including Python, coding, curve-fitting, and error propagation
│   └── computing_environment.md: instructions for setting up your computing environment
└── velazquez_lab/: folder containing all Python modules
    ├── eis/: electrochemical impedance spectroscopy tools
    ├── gc/: gas chromatography tools
    ├── nmr/: nuclear magnetic resonance tools
    ├── pol/: polarization curve tools
    │   ├── julius/: newly implemented Tafel slope method
    │   └── legacy/: code used for previous calculations of Tafel slope
    └── utils/: utilities used throughout project
```
