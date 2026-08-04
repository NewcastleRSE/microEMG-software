# microemggui

PySide6 GUI wizard for analysing multi-channel microEMG recordings. Wraps the [`pymicroemg`](../pymicroemg) analysis library in a step-by-step interface covering data loading, preprocessing, motor unit identification, muscle fibre localisation, and jitter analysis for diagnosing myasthenia gravis and congenital myasthenic syndromes.

## Install

Both microemggui and pymicroemg need to be installed:

```
pip install "git+https://github.com/NewcastleRSE/microEMG-software.git@main#subdirectory=analysis_software/microemggui"
pip install "git+https://github.com/NewcastleRSE/microEMG-software.git@main#subdirectory=analysis_software/pymicroemg"
```

The @main tag can be replaced with a different branch name if you would like to install a different version.

Requires Python 3.11 or 3.12.

## Launch

```
microemggui
```

On first launch, if the demo recording is not present, the GUI will prompt to download it (~1 GB) from the GitHub release. The data is cached in the OS user data directory (`~/Library/Application Support/microEMG/` on macOS) so subsequent launches skip the prompt.

## GUI instructions

A help guide is bundled in the GUI — click the help icon in the toolbar. A PDF copy is also available at [`microemggui/docs/microemg_help_guide.pdf`](microemggui/docs/microemg_help_guide.pdf).

## More information

- [Top-level repository](https://github.com/NewcastleRSE/microEMG-software)
- [Analysis library (`pymicroemg`)](../pymicroemg)
- [API documentation](https://newcastlerse.github.io/microEMG-software/)
