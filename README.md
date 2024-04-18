# microEMG-software
Software for recording and analysing microEMG recordings, developed for "Multi-channel jitter recordings in the diagnosis of myasthenia gravis and congenital myasthenic syndromes" project.

## About

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed sollicitudin ante at eleifend eleifend. Sed non vestibulum nisi. Aliquam vel condimentum quam. Donec fringilla et purus at auctor. Praesent euismod vitae metus non consectetur. Sed interdum aliquet nisl at efficitur. Nulla urna quam, gravida eget elementum eget, mattis nec tortor. Fusce ut neque tellus. Integer at magna feugiat lacus porta posuere eget vitae metus.

Curabitur a tempus arcu. Maecenas blandit risus quam, quis convallis justo pretium in. Suspendisse rutrum, elit at venenatis cursus, dolor ligula iaculis dui, ut dignissim enim justo at ligula. Donec interdum dignissim egestas. Nullam nec ultrices enim. Nam quis arcu tincidunt, auctor purus sit amet, aliquam libero. Fusce rhoncus lectus ac imperdiet varius. Sed gravida urna eros, ac luctus justo condimentum nec. Integer ultrices nibh in neque sagittis, at pretium erat pretium. Praesent feugiat purus id iaculis laoreet. Proin in tellus tristique, congue ante in, sodales quam. Sed imperdiet est tortor, eget vestibulum tortor pulvinar volutpat. In et pretium nisl.

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

[Git Large File Storage](https://git-lfs.com/) to store demo recordings (see page for installation instructions). Use ```git lfs ls-files``` to check which files are tracked using Git LFS.

### Installation

First install poetry in your Python environment:

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

### Running Locally

How to run the application on your local system.

### Running Tests

How to run tests on your local system.

## Deployment

### Local

### Production

Deploying to the production system. Examples of this would include cloud, HPC or virtual machine. 

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
