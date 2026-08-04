# microEMG-software

Software for recording and analysing microEMG recordings, developed for "Multi-channel jitter recordings in the diagnosis of myasthenia gravis and congenital myasthenic syndromes" project.

## About

In clinical practice, electromyography (EMG) is performed using a single-channel electrode to capture motor unit and muscle fibre potentials. These recordings are subsequently analysed to detect abnormalities in motor unit function. Clinicians must currently obtain multiple single-channel recordings which is time-consuming and requires expertise. Additionally, a single-channel recording does not provide information about muscle fibre locations or motor unit sizes.

To address these limitations, the microEMG team has developed:

1. A multichannel EMG (microEMG) electrode. Each electrode contains 32 or 64 channels, allowing clinicians to obtain a single, multivariate recording per muscle.
2. An analytical pipeline that identifies motor units and localises muscle fibres.

These Python modules provide classes and a user interface for analysing microEMG recordings.

_Examples using the microEMG GUI to analyse 60s of data from the demo recording - see [docs/gui_screenshots](docs/gui_screenshots) for more steps._

<p align="center">
  <a href="docs/gui_screenshots/04_preprocess02.png">
    <img
      src="docs/gui_screenshots/04_preprocess02.png"
      alt="Preprocessing page of the microEMG GUI, showing a preprocessed recording and preprocessing settings."
      width="360">
  </a>
  &nbsp;
  <a href="docs/gui_screenshots/07_selectmu.png">
    <img
      src="docs/gui_screenshots/07_selectmu.png"
      alt="Page for selecting motor units in the microEMG GUI, showing four motor units and the potentials of motor unit 2."
      width="360">
  </a>
</p>

<p align="center">
  <a href="docs/gui_screenshots/08_localise02.png">
    <img
      src="docs/gui_screenshots/08_localise02.png"
      alt="Page for localising muscle fibres in the microEMG GUI, showing localisation of five fibres for motor unit 3."
      width="360">
  </a>
  &nbsp;
  <a href="docs/gui_screenshots/09_jitter02.png">
    <img
      src="docs/gui_screenshots/09_jitter02.png"
      alt="Page for analysing jitter in the microEMG GUI, showing two muscle fibres in motor unit 2 with a mean consecutive difference of 37 microseconds."
      width="360">
  </a>
</p>

### Project Team

Dr Roger Whittaker, Newcastle University ([roger.whittaker@newcastle.ac.uk](mailto:roger.whittaker@newcastle.ac.uk))  
Dr Stuart Maitland, Newcastle University ([stu.maitland@newcastle.ac.uk](mailto:stu.maitland@newcastle.ac.uk))

Dr Gabrielle Schroeder, Newcastle University ([gabrielle.schroeder@newcastle.ac.uk](mailto:gabrielle.schroeder@newcastle.ac.uk))  
Dr Richard Howey, Newcastle University ([richard.howey@newcastle.ac.uk](mailto:richard.howey@newcastle.ac.uk))  
Dr Frances Turner, Newcastle University ([frances.hutchings@newcastle.ac.uk](mailto:frances.hutchings@newcastle.ac.uk))

### RSE Contact

Gabrielle Schroeder
RSE Team  
Newcastle University  
([gabrielle.schroeder@newcastle.ac.uk](mailto:gabrielle.schroeder@newcastle.ac.uk))

## Built With

[Python 3.11](https://www.python.org/)  
[PySide6](https://www.qt.io/qt-for-python)

The microEMG GUI uses  
[Bootstrap Icons](https://icons.getbootstrap.com/)  
[CartoColors](https://carto.com/carto-colors/) (via the [palettable](https://jiffyclub.github.io/palettable/) Python package)

## Getting Started

### Prerequisites

Developed and tested using Python 3.11

Dependencies are managed using Python package [Poetry](https://python-poetry.org/), version 1.4.0

See pyproject.toml file for list of Python package dependencies.

#### Development tools

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) as a formatter

[mypy](https://mypy.readthedocs.io/en/stable/) as a static type checker

[Flake8](https://flake8.pycqa.org/en/latest/) (including the [bugbear](https://github.com/PyCQA/flake8-bugbear) plugin) as a linter

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit) for running checks on committed code (run `pre-commit install` to use the included pre-commit hooks)

### Installation

#### External users (pip install from GitHub)

Install the GUI and analysis library together (recommended):

```
pip install "git+https://github.com/NewcastleRSE/microEMG-software.git@main#subdirectory=analysis_software/pymicroemg"
pip install "git+https://github.com/NewcastleRSE/microEMG-software.git@main#subdirectory=analysis_software/microemggui"
```

Or install the analysis library only (no GUI):

```
pip install "git+https://github.com/NewcastleRSE/microEMG-software.git@main#subdirectory=analysis_software/pymicroemg"
```

The @main tag can be replaced with a different branch name if you would like to install a different version.

Requires Python 3.11 or later.

#### Contributors / developers (clone + poetry)

Clone the repository from GitHub, then install `poetry` in your global environment - we used version 1.4.0:

```
pip install poetry==1.4.0
```

Create a Python 3.11+ environment and [install the packages using poetry](https://python-poetry.org/docs/basic-usage/#installing-dependencies) (run from within the project directory):

```
poetry install
```

`poetry` will install both the Python package dependencies and set up paths to the local packages, [`pymicroemg`](analysis_software/pymicroemg/pymicroemg) and [`microemggui`](analysis_software/microemggui/microemggui).
See the **Troubleshooting** section for more help with `poetry`.

An example EMG recording is available as a release asset and is downloaded on demand — see [Demo recording](#demo-recording) below.

### Running Locally

#### MicroEMG GUI

To launch the GUI from within the installed Python environment, use the terminal command

```
microemggui
```

If you are running from a cloned repo with `poetry install`, you can also use:

```
python -m microemggui
```

On first launch, if the demo recording is not present, the GUI will prompt to download it (~1 GB) from the [v0.1.0 release](https://github.com/NewcastleRSE/microEMG-software/releases/tag/v0.1.0). The download is cancellable and the data is cached in the OS user data directory (`~/Library/Application Support/microEMG/` on macOS) so subsequent launches skip the prompt.

Subsections of the GUI can also be run using the other Python files in [`gui_dev`](gui_dev) (e.g., from the repository's root, run `python gui_dev/gui_dev_main.py`).

GUI instructions are [here](analysis_software/microemggui/microemggui/docs/microemg_help_guide.pdf) - this document can also be accessed via the help icon in the GUI.

The GUI has been developed on MacOS and may have some missing functionality or altered formats on other operating systems.

The GUI produces log messages in `microemggui.log`, written to the OS user log directory (`~/Library/Logs/NewcastleRSE/microEMG/` on macOS). The log is rotated automatically so previous sessions are preserved.

#### MicroEMG analysis scripts

Alternatively, you can develop your own analysis scripts using the `pymicroemg` module for additional control over analysis settings and steps. See [`data_analysis/example_pipeline.py`](data_analysis/example_pipeline.py) for an example pipeline.

#### Demo recording

The demo recording (~1 GB) is downloaded on demand rather than shipped in the repository. It is stored in the OS user data directory under `recordings/64-channel/demo1/`:

| OS      | Location                                                        |
|---------|-----------------------------------------------------------------|
| macOS   | `~/Library/Application Support/microEMG/recordings/64-channel/demo1/` |
| Linux   | `~/.local/share/microEMG/recordings/64-channel/demo1/`          |
| Windows | `C:\Users\<user>\AppData\Local\NewcastleRSE\microEMG\recordings\64-channel\demo1\` |

To fetch it programmatically (outside the GUI):

```python
from pymicroemg.demo_data import download_and_extract_demo
download_and_extract_demo()
```

`pymicroemg.helper_config.get_recording_path_and_id(0)` raises `DemoDataMissingError` if the demo has not yet been downloaded.

To remove the demo data and free disk space, delete the `demo1/` folder at the path above (e.g. `rm -rf "~/Library/Application Support/microEMG/recordings/64-channel/demo1"` on macOS). The GUI will prompt to re-download it on next launch.

### Software structure

We developed two packages:

- [`pymicroemg`](analysis_software/pymicroemg/pymicroemg) contains functions and classes for analysing microEMG data.
- [`microemggui`](analysis_software/microemggui/microemggui) is built on top of `pymicroemg` to provide a graphical user interface (GUI) for performing the analysis, with the ability to modify some analysis settings.

#### pymicroemg module

The `pymicroemg` module is documented using `pdoc` [in the docs directory](docs/), and an overview of the methods is provided [here](docs/Analysis-report.docx). You can view the `pdoc` documentation at the repository's GitHub page, [https://newcastlerse.github.io/microEMG-software/](https://newcastlerse.github.io/microEMG-software/). Alternatively, download the entire folder (or cloning the repository) and open [pymicroemg.html](docs/pymicroemg.html) - it will open in web browser.

If you update the `pymicroemg` module, please update the documentation by running

```
pdoc --docformat numpy pymicroemg -o ./docs
```

from a terminal from the root directory.

#### microemggui module

The [`widgets`](analysis_software/microemggui/microemggui/widgets) submodule contains the widgets for the GUI, organised by the "pages" in the GUI (one page per analysis step).
The full GUI is specified in [widgets/main/main_window.py](analysis_software/microemggui/microemggui/widgets/main/main_window.py).

The [`models`](analysis_software/microemggui/microemggui/models) submodule contains "models", or interfaces, to some of the `pymicroemg` classes for settings and data.
This approach makes it easier to separate GUI functionality from the underlying analysis software. Note that many of the settings options (e.g., options for dropdown boxes) for the GUI are specified in [`models/settings.py`](analysis_software/microemggui/microemggui/models/settings.py).

The [`docs`](analysis_software/microemggui/microemggui/docs) folder contains a PDF with GUI instructions, [`microemg_help_guide.pdf`](analysis_software/microemggui/microemggui/docs/microemg_help_guide.pdf). This PDF can be manually updated using the associated Word Document. It is linked to a help icon in the GUI.

The [`styles`](analysis_software/microemggui/microemggui/styles) submodule contains a style sheet for modifying the GUI's appearance and code for implementing the style sheet.

The [`icons`](analysis_software/microemggui/microemggui/icons) submodule contains icons (mostly [Bootstrap](https://icons.getbootstrap.com/)) used in the GUI.
These icons are set up using a [Qt resource system](https://www.pythonguis.com/tutorials/packaging-data-files-pyside6-with-qresource-system/) to ensure they are not dependent on a specific directory structure or paths.
If you change the icons, you need to update the resource system by running this command from the root directory in a terminal:

```
pyside6-rcc analysis_software/microemggui/microemggui/icons/icons.qrc -o analysis_software/microemggui/microemggui/icons/icons.py
```

### Running Tests

The `microemggui` has partial test coverage using `pytest`. These tests can be run from a terminal using

```
pytest analysis_software/microemggui/
```

## Deployment

### Building a GUI executable

The GUI can be packaged into an executable using `pyinstaller` and the `microemggui.spec` file in the `microemggui` package - from the repository's root, run the terminal command

```
cd analysis_software/microemggui/microemggui
poetry run pyinstaller --workpath ../../../build/microemggui --distpath ../../../dist/microemggui microemggui.spec
```

`pyinstaller` will create `build` and `dist` directories in the repository's root - the executable will be `dist/microemggui/microemggui`. It may take a minute or two to launch when opened.

### Troubleshooting

- If you ran the installation instructions outside of a virtual environment, poetry will have created one for you when you ran `poetry install`, however it won't have activated it automatically. You can activate the virtual environment with `poetry shell` and exit this with the command `exit`. Outside of this virtual environment you will not have the required installed dependencies so this can be a cause of errors.

- For Linux users, an error has been noted when trying to run the GUI where the QT platform plugin fails to load. [This thread](https://stackoverflow.com/questions/77725761/from-6-5-0-xcb-cursor0-or-libxcb-cursor0-is-needed-to-load-the-qt-xcb-platform) proposes a solution that worked in our testing, to install libxcb-cursor-dev.

## Usage

- [`pymicroemg` documentation](https://newcastlerse.github.io/microEMG-software/)
- [GUI instructions](analysis_software/microemggui/microemggui/docs/microemg_help_guide.pdf)
- [MicroEMG analysis methods](docs/Analysis-report.docx)
- [Intan recording format](docs/Intan_RHD2000_data_file_formats.pdf)

## Roadmap

- [ ] Initial Research
- [x] Minimum viable product <-- You are Here
- [ ] Alpha Release
- [ ] Feature-Complete Release

### Suggested software improvements

- Extend test coverage of `microemggui` and add unit tests for `pymicroemg`
- Modify `pymicroemg` settings classes to validate settings attributes when modified by the user and prevent direct access to settings attributes (e.g., using [getters and setters](https://realpython.com/python-getter-setter/))
- Type hints have been implemented, but not fully validated using `mypy` (a static type checker)
- [Package GUI](https://www.pythonguis.com/tutorials/packaging-pyside6-applications-windows-pyinstaller-installforge/)
- Improve and test GUI implementation on Windows and Linux
- Update CI to 1) automatically update documentation (GUI PDF and `pymicroemg` `pdoc` documentation) and the Qt resource system when necessary and 2) include testing and static type checking in pull request checks.

Additional potential features are organised using the associate project board and issues.

## Contributing

### Main Branch

Protected and can only be pushed to via pull requests. It should be considered stable and a representation of production code.

### Dev Branch

Should be considered fragile; code should compile and run, but features may be prone to errors.

### Feature Branches

A branch per feature that is being worked on.

https://nvie.com/posts/a-successful-git-branching-model/

### Package management

Adding new packages:

1. `poetry add <package name>` which adds a package to the pyproject.toml file (the list of requirements)

To add a package to a specific group, e.g. dev: `poetry add <package name> -G dev`

2. `poetry lock --no-update` updates the lock file (with all the packages needed and the exact versions, including dependencies of the packages in the pyproject.toml file), but does not change the version of the previously tracked dependencies

## License

This project is licensed under the GNU General Public License v3.0 — see the [LICENSE](LICENSE) file for details.

Third-party components bundled with this project retain their original licenses; see [NOTICE](NOTICE) for attributions.

## Citation

Please cite the associated paper if you use this code:

Stuart Maitland, Enrique Escobedo-Cousin, Ian Schofield, Anthony O'Neill, Stuart Baker, Roger Whittaker,
_Electrical cross-sectional imaging of human motor units in vivo_,
Clinical Neurophysiology, Volume 136, 2022, Pages 82-92, ISSN 1388-2457,
https://doi.org/10.1016/j.clinph.2021.12.022
([ScienceDirect link](https://www.sciencedirect.com/science/article/pii/S1388245722000244))

```
@article{maitland2022electrical,
  title   = {Electrical cross-sectional imaging of human motor units in vivo},
  author  = {Maitland, Stuart and Escobedo-Cousin, Enrique and Schofield, Ian and O'Neill, Anthony and Baker, Stuart and Whittaker, Roger},
  journal = {Clinical Neurophysiology},
  volume  = {136},
  pages   = {82--92},
  year    = {2022},
  issn    = {1388-2457},
  doi     = {10.1016/j.clinph.2021.12.022}
}
```
