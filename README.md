# Graphs from Game Cameras

Python modules for generating animal social networks using game camera data.

## Requirements

1. [exiftool](http://www.sno.phy.queensu.ca/~phil/exiftool/)
2. [Python 2.7.5](https://www.python.org/download/releases/2.7.5/) (should work with Python 2.7.x)
3. Python modules

	a. [pandas](http://pandas.pydata.org/)
	
	b. [pyexif](https://smarnach.github.io/pyexiftool/)

## Installation

These are stand-alone scripts requiring no separate installation.

## Modules

### get_timestamps.py

Game camera photo EXIF time stamp retrieval.

| Argument | Details |
|---|---|
|`-f (--file)` | CSV file containing paths to photos and animal IDs |
|`-ot (--output_time)` | Path for writing output time stamp data |

### generate_graphs.py

Graph generation from time stamp and animal ID data.

| Argument | Details |
|---|---|
|`-f (--file)` | CSV file containing animal IDs and time stamps (may be output of get_timestamps.py) |
|`-w (--window)` | Window size for aggregating temporal data |
|`-u (--units)` | Units for window size, if not hours. Acceptable entries are T (minutes), H (hours), and D (days) |
|`-og (--output_graph)` | Path for writing output graph image (default = None) |

## Example Usage

Retrieve time stamps from a single camera trap site:

	python get_timestamps.py -f site1_data.csv -ot site1_times.csv

Generate network for camera trap site based on hourly co-occurrence intervals:

	python generate_graphs.py -f site1_times.csv -w 1 -u H -og site1_graph.png
