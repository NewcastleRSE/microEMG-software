# microEMG-software
Software for recording and analysing microEMG recordings, developed for "Multi-channel jitter recordings in the diagnosis of myasthenia gravis and congenital myasthenic syndromes" project.

## About

In clinical practice, electromyography (EMG) is performed using a single-channel electrode to capture motor unit and muscle fibre potentials. These recordings are subsequently analysed to detect abnormalities in motor unit function. Clinicians must currently obtain multiple single-channel recordings which is time-consuming and requires expertise. Additionally, a single-channel recording does not provide information about muscle fibre locations or motor unit sizes.

To address these limitations, the microEMG team have developed:

1. A multichannel EMG (microEMG) electrode. Each electrode contains 32 or 64 channels, allowing clinicians to obtain a single, multivariate recording per muscle.
2. An analytical pipeline that identifies motor units and localises muscle fibres. 


The microEMG team’s primary goal is for their microEMG electrode technology and analysis pipeline to be obtained by an external company that will commercialise these techniques.
 
To meet this goal, the microEMG team requires RSE team assistance in the following: 

1.	Development of a real-time recording GUI for EMG recordings with multiple channels. 
2.	Development of analysis scripts and GUI to allow clinicians to perform microEMG recording analyses within a reasonable runtime. 
3.	The microEMG team will conduct a small pilot study to collect microEMG data from patients with neuromuscular disorders. The current analytical pipeline needs to be extended to describe more features of the patients’ motor units, and the data from all patients will need to be analysed using the updated software.

See project documentation for a detailed description.

### Project Team

Dr Roger Whittaker, Newcastle University  ([roger.whittaker@newcastle.ac.uk](mailto:roger.whittaker@newcastle.ac.uk))  
Dr Stuart Maitland, Newcastle University  ([stu.maitland@newcastle.ac.uk](mailto:stu.maitland@newcastle.ac.uk))  

Dr Gabrielle Schroeder, Newcastle University ([gabrielle.schroeder@newcastle.ac.uk](mailto:gabrielle.schroeder@newcastle.ac.uk))  
Dr Richard Howey, Newcastle University ([richard.howey@newcastle.ac.uk](mailto:richard.howey@newcastle.ac.uk))

### RSE Contact
Gabrielle Schroeder
RSE Team  
Newcastle University  
([gabrielle.schroeder@newcastle.ac.uk](mailto:gabrielle.schroeder@newcastle.ac.uk))  

## Built With

This section is intended to list the frameworks and tools you're using to develop this software. Please link to the home page or documentation in each case.

[Python 3.11](https://www.python.org/)  
[PySide6](https://www.qt.io/qt-for-python)  
[Framework 3](https://something.com)  

## Getting Started

### Prerequisites

Developed using Python 3.11

Dependencies are managed using Python package [Poetry](https://python-poetry.org/), version 1.4.0

See pyproject.toml file for list of Python package dependencies.


#### Development tools

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) as a formatter

[mypy](https://mypy.readthedocs.io/en/stable/) as a static type checker

[Flake8](https://flake8.pycqa.org/en/latest/) (including the [bugbear](https://github.com/PyCQA/flake8-bugbear) plugin) as a linter

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit) for running checks on committed code (run `pre-commit install` to use the included pre-commit hooks)


### Installation

After ensuring you have the project frameworks installed (PySide6, Python 3.11+), install poetry in your Python environment:

Using pip:
```
pip install poetry==1.4.0
```

Alternatively, using [Anaconda](https://anaconda.org/):
```
conda install poetry==1.4.0
```

Next, [install the packages using poetry](https://python-poetry.org/docs/basic-usage/#installing-dependencies) (run within the project directory):

```
poetry install
```

Example recording data needs to be manually added in a "recordings" folder at the root level. See the paths in helper_config.py in pymicroemg. These paths are the same as in the provided data, with the exception that the "64 channel" directory is replaced with "64-channel".

### Running Locally

To run the user interface during development testing, open a terminal and navigate to the `gui_dev` folder, then enter `python gui_dev_main.py` and the user interface should appear.

Adding new packages: 
1. `poetry add <package name>` which adds a package to the pyproject.toml file (the list of requirements)

To add a package to a specific group, e.g. dev: `poetry add <package name> -G dev` 

2. `poetry lock --no-update` updates the lock file (with all the packages needed and the exact versions, including dependencies of the packages in the pyproject.toml file), but does not change the version of the previously tracked dependencies


### Running Tests

How to run tests on your local system.

## Deployment

### Local

### Production

Deploying to the production system. Examples of this would include cloud, HPC or virtual machine. 

### Troubleshooting
 
- If you ran the installation instructions outside of a virtual environment, poetry will have created one for you when you ran `poetry install`, however it won't have activated it automatically. You can activate the virtual environment with `poetry shell` and exit this with the command `exit`. Outside of this virtual environment you will not have the required installed dependencies so this can be a cause of errors.

- For linux users an error has been noted when trying to run the GUI where the QT platform plugin fails to load. [This thread](https://stackoverflow.com/questions/77725761/from-6-5-0-xcb-cursor0-or-libxcb-cursor0-is-needed-to-load-the-qt-xcb-platform) proposes a solution that worked in our testing, to install libxcb-cursor-dev.


## Usage

Any links to the production environment, video demos and screenshots.

## Roadmap

- [x] Initial Research  
- [ ] Minimum viable product <-- You are Here  
- [ ] Alpha Release  
- [ ] Feature-Complete Release  

## Contributing

### Main Branch
Protected and can only be pushed to via pull requests. It should be considered stable and a representation of production code.

### Dev Branch
Should be considered fragile; code should compile and run, but features may be prone to errors.

### Feature Branches
A branch per feature that is being worked on.

https://nvie.com/posts/a-successful-git-branching-model/

## License

## Citation

Please cite the associated papers for this work if you use this code:

```
@article{xxx2023paper,
  title={Title},
  author={Author},
  journal={arXiv},
  year={2023}
}
```


## Acknowledgements
This work was funded by a grant from the UK Research Councils, EPSRC grant ref. EP/L012345/1, “Example project title, please update”.
