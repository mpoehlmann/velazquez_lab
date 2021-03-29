Dataset Title:

CO2 Reduction Tafel Dataset for Bayesian Data Analysis


Description:

This dataset contains 344 different digitized and tagged Tafel slope datasets from the CO2 reduction literature. We re-analyze this data with a Bayesian data analysis procedure that estimates a Tafel slope and yields distributional uncertainty information about its value. We are releasing this dataset along with our study to facilitate re-analyzing and refitting our data using different models and approaches.


Author Information:

Aditya M. Limaye
Department of Chemical Engineering, MIT, Cambridge MA 02139
amlimaye -SYMBOL- mit -SYMBOL- edu

Joy S. Zeng
Department of Chemical Engineering, MIT, Cambridge MA 02139
jszeng -SYMBOL- mit -SYMBOL- edu

Adam P. Willard
Department of Chemistry, MIT, Cambridge MA 02139
awillard -SYMBOL- mit -SYMBOL- edu

Karthish Manthiram
Department of Chemical Engineering, MIT, Cambridge MA 02139
karthish -SYMBOL- mit -SYMBOL- edu

(SYMBOL replacements should be self-evident)


Date of Collection: October 2019 - May 2020


File Tree:

├── README                                  -- this file
├── data_organization.pdf                   -- PDF including data organization and citations for data
├── julius                                  -- directory for analysis code
│   ├── LICENSE                             -- license file for code
│   ├── bin
│   │   ├── cli.py                          -- cmdline entry point for fitting workflow
│   │   └── process-annotated-links.py      -- used to generate dataframe consumed by fitting workflow
│   ├── lib-python
│   │   └── julius                          -- Python module called by fitting workflow
│   │       ├── __init__.py
│   │       ├── fits.py
│   │       ├── models.py
│   │       ├── records.py
│   │       ├── utils.py
│   │       └── visualization.py
│   └── requirements.txt
├── records                                 -- directory containing data and metadata files
└── records.txt                             -- plain text record of the directories in the records/ directory. column names are specified in the first line, but this file is only meant to be used for processing by the julius/cli.py workflow entry point. A human-readable record of the provenance of all papers can be found in data_organization.pdf.


Licensing:

The code in the julius package is distributed under the MIT License, described by the LICENSE file in the julius directory.

The data in the records directory is distributed under a CC BY 4.0 License, described by the LICENSE file in the records directory.

Cite the code and data as: Aditya M. Limaye, Joy S. Zeng, Adam P. Willard, Karthish Manthiram. (2020) CO2 Reduction Tafel Dataset for Bayesian Data Analysis. Zenodo. DOI: 10.5281/zenodo.3995021

Note that the CC BY License does not apply to the PNG images distributed along with the records. The figures are licensed to reuse under the agreement between MIT and the publishers of the articles ( https://libraries.mit.edu/scholarly/publishing/using-published-figures/ ). Citations for all articles are included in the data_organization.pdf file.


Organization of data in records directory:

Organizational information of the data in the records directory is included in the data_organization.pdf file.


Instructions for running fits:

(1) Install all Python package dependencies. This is done using the pip package manager. You can do this inside a new virtual environment if you don't want to pollute your current Python environment. From the top-level directory, run:

> pip3 install $(cat julius/requirements.txt)

(2) Prepare a dataframe from the annotated links file. This dataframe assigns a unique identifier to each dataset, and will be consumed by the fitting workflow manager. From the top-level directory, run:

> julius/bin/process-annotated-links.py --links-fname data/records.txt --df-out-fname data/records-df.pkl

(3) Dispatch the fits. From the top-level directory, run:

> julius/bin/cli.py dispatch-fits --records-dir data/records --df-name data/records-df.pkl --save-dir fits --rand-seed 2020 --nsamples 10000

(4) Generate plots for each of the fits to facilitate further examination and analysis

> julius/bin/cli.py plot-fits --records-dir data/records --df-name data/records-df.pkl --fits-dir fits --figures-dir figures
