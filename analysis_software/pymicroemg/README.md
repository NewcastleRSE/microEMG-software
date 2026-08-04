# pymicroemg

Python analysis library for multi-channel microEMG recordings. Provides a pipeline for loading raw Intan `.rhd` data, preprocessing, motor unit identification, muscle fibre localisation, and jitter analysis for diagnosing myasthenia gravis and congenital myasthenic syndromes. For a graphical interface over this library, see [`microemggui`](../microemggui).

## Install

```
pip install "git+https://github.com/NewcastleRSE/microEMG-software.git@main#subdirectory=analysis_software/pymicroemg"
```

The @main tag can be replaced with a different branch name if you would like to install a different version.

Requires Python 3.11 or 3.12.

## Quick start

```python
from pymicroemg import (
    EMGFiles, EMGPreprocSettings, EMGAnalysisReconstructSettings
)

emg_files = EMGFiles("/path/to/recording")
emg_raw = emg_files.load_emg_data()

settings = EMGPreprocSettings()
settings.add_butterworth_filter(filter_type="bandpass", cutoff_freq=[100, 400], order=4)
emg_preproc = emg_raw.preprocess(settings)

reconstruct_settings = EMGAnalysisReconstructSettings()
analysis = emg_preproc.reconstruct(reconstruct_settings)
```

See [`data_analysis/example_pipeline.py`](../../data_analysis/example_pipeline.py) in the top-level repo for a full end-to-end example, and the [API docs](https://newcastlerse.github.io/microEMG-software/) for details.

## Demo data

A demo recording (~1 GB) can be downloaded programmatically:

```python
from pymicroemg.demo_data import download_and_extract_demo
download_and_extract_demo()
```

## More information

- [Top-level repository](https://github.com/NewcastleRSE/microEMG-software)
- [API documentation](https://newcastlerse.github.io/microEMG-software/)
- [GUI package (`microemggui`)](../microemggui)
