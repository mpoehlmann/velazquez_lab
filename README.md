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

Activate your conda environment:
```bash
setup_conda
```

## Project structure
├── ``environment.yml``: file used to create ``conda`` computing environment
├── ``README.txt``: important project information and instructions
├── ``eis/``: electrochemical impedance spectroscopy tools
├── ``gc/``: gas chromatography tools
├── ``pol/``: polarization curve tools
│   ├── ``julius/``: newly implemented Tafel slope method
│   └── ``legacy/``: code used for previous calculations of Tafel slope
├── ``tutorials/``: a collection of useful tutorials on topics including Python, coding, curve-fitting, and error propagation
│   └── ``computing_environment.md``: instructions for setting up your computing environment
└── ``utils/``: utilities used throughout project