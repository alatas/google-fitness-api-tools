#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Reads weight data from Google Fitness API and export to a CSV file

Usage: weight-exporter.py [-h] [-o OUTPUT_FILE] [-s START_DATE] [-e END_DATE]
                          [-c COLUMN_SEPARATOR]

Optional arguments:
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

Sample usage:

  $ python weight-exporter.py -s 2017-12-01 -e 2018-03-20

'''

import sys
import argparse
import csv
from datetime import datetime
from googleapiclient import sample_tools


ARGPARSER = argparse.ArgumentParser(description='Reads weight data from Google Fitness API and export to a CSV file')
ARGPARSER.add_argument('-o', '--output-file', type=str,
                       help=('Output file path. (default = google-fit-weight-XXX.csv)'),
                       default='google-fit-weight-' + datetime.now().strftime('%s') + '.csv')
ARGPARSER.add_argument('-s', '--start-date', type=str,
                       help=('Start date of the requested date range in '
                             'YYYY-MM-DD format. (default = 2010-01-01)'), default='2010-01-01')
ARGPARSER.add_argument('-e', '--end-date', type=str,
                       help=('End date of the requested date range in '
                             'YYYY-MM-DD format. (default = 2020-01-01)'), default='2020-01-01')
ARGPARSER.add_argument('-c', '--column-separator', type=str,
                       help=('Column separator for output file. (default tab)'), default='\t')

def main(argv):
  argparsed = ARGPARSER.parse_args(argv[1:])

  try:
    start_date = datetime.strptime(argparsed.start_date.strip(), '%Y-%m-%d')
    end_date = datetime.strptime(argparsed.end_date.strip(), '%Y-%m-%d')
  except:
    ARGPARSER.print_help()
    exit(-1)

  print 'Export values between %s and %s\n' % (start_date.strftime('%a, %d %b %Y'), end_date.strftime('%a, %d %b %Y'))

  print 'Creating API Service'
  service, flags = sample_tools.init(
      [], 'fitness', 'v1', __doc__, __file__,
      scope='https://www.googleapis.com/auth/fitness.body.read')

  print 'Fetching Google Fit Weight Data Sources'
  datasources = service.users().dataSources().list(
      userId='me', dataTypeName='com.google.weight'
  ).execute()

  print 'Fetching Google Fit Weight Dataset'
  dataset = service.users().dataSources().datasets().get(
      userId='me', dataSourceId='derived:com.google.weight:com.google.android.gms:merge_weight',
      datasetId=to_nano_epoch(start_date) + '-' + to_nano_epoch(end_date)
  ).execute()

  line_count = 0

  print 'Exporting Google Fit Weight Dataset (expected %d row)' % len(dataset['point'])
  with open(argparsed.output_file, 'wb') as csv_out:
    fields = ['Source', 'Value(kg)', 'Date', 'Year', 'Month', 'Day', 'Hour', 'Minute', 'Second']
    writer = csv.DictWriter(csv_out, fieldnames=fields, delimiter='\t')
    writer.writeheader()

    for point in dataset['point']:
      out_data = json_to_row(datasources, point)
      line_count += 1
      writer.writerow(out_data)

  print '\nTotal %d value extracted to %s' % (
      line_count, argparsed.output_file)


def json_to_row(datasources, point):
  point_date = from_nano_epoch(float(point['startTimeNanos']))
  point_value = round(point['value'][0]['fpVal'], 1)

  out_data = {
      'Source': data_source_name(datasources, point['originDataSourceId']),
      'Value(kg)': point_value,
      'Date': point_date.isoformat(),
      'Year': point_date.year,
      'Month': point_date.month,
      'Day': point_date.day,
      'Hour': point_date.hour,
      'Minute': point_date.minute,
      'Second': point_date.second}
  return out_data


def data_source_name(datasources, datastreamid):
  ds = (s for s in datasources['dataSource'] if s['dataStreamId'] == datastreamid).next()
  if ds is None:
    return 'Unknown Application'
  else:
    out = []
    if 'application' in ds and 'packageName' in ds['application']:
      out.append(ds['application']['packageName'])
    if 'device' in ds and 'manufacturer' in ds['device']:
      out.append(ds['device']['manufacturer'])
    if 'device' in ds and 'model' in ds['device']:
      out.append(ds['device']['model'])
    return ' '.join(out)


def from_nano_epoch(nanotime):
  return datetime.fromtimestamp(round(nanotime / 1000000000))


def to_nano_epoch(inpdate):
  return str(int(inpdate.strftime('%s')) * 1000000000)


if __name__ == '__main__':
  main(sys.argv)
