# Radarr Stalled Cleaner

Radarr Stalled Cleaner is a Python script that helps manage movie downloads in a Radarr queue. It checks the estimated remaining time and the time elapsed since a movie was grabbed. If the remaining time or the elapsed time exceed specified limits, the script will remove the movie from the queue.

## Features

- Automatically remove slow downloads from the Radarr queue.
- Remove downloads that have been in the queue for too long.
- Customizable time limits for remaining and elapsed time.

## Installation

1. Make sure you have Python 3.9.13 or higher installed.
2. Install the package using pip, it should automatically install the required dependencies:

```bash
pip install .
```

3. Install the package.

## Developement

The Makefile is used to manage the development and testing. It defines several targets that can be used to build, test, and clean the project.

### `clean`

This target removes all generated files, including the virtual environment and build artifacts.

```sh
make clean
```

### `venv`

This target creates a Python virtual environment in the `.venv` directory. It will install all dependencies the package needs.

```sh
make venv
```

### `launch`

This target runs the radarr script. Make sure to have configured `host_url` and `api_key`

```sh
make launch
```

### `test`

This target runs the tests for the package.

```sh
make test
```

## Configuration

Open the script file and update the following variables with your Radarr host URL and API key:

```python
host_url = 'address:port'
api_key = 'your_radarr_api_key_here'
```

You can also customize the time limits for remaining and elapsed time:

```python
time_limit = tdelta(hours=0, days=2)
when_to_start_checking_time_remaining = tdelta(hours=1, days=0)
max_allowed_time_remaining = tdelta(hours=0, days=1)
```

## Usage

Simply run the script from your command line:

```bash
python src/RadarrStalledCleaner.py
```

or 

```sh
make launch
```

## Authors

- Dako Dimov
- Lyuboslav Angelov
