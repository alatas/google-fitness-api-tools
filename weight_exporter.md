# Weight Exporter
Reads weight data from Google Fitness API and export to a CSV file

## Usage:
```sh
weight-exporter.py [-h] [-o OUTPUT_FILE] [-s START_DATE] [-e END_DATE] [-c COLUMN_SEPARATOR]
```

## Optional arguments:
```
-h, --help            show this help message and exit
-o OUTPUT_FILE, --output-file OUTPUT_FILE
                      Output file path. (default = google-fit-weight-
                      XXX.csv)
-s START_DATE, --start-date START_DATE
                      Start date of the requested date range in YYYY-MM-DD
                      format. (default = 2010-01-01)
-e END_DATE, --end-date END_DATE
                      End date of the requested date range in YYYY-MM-DD
                      format. (default = 2020-01-01)
-c COLUMN_SEPARATOR, --column-separator COLUMN_SEPARATOR
                      Column separator for output file. (default tab)
```

## Sample usage:

```sh
$ python weight-exporter.py -s 2017-12-01 -e 2018-03-20
```