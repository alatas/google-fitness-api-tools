#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''Reads weight data from Google Fitness API and export to a CSV file

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Output file path. (default = google-fit-weight-
                        XXX.csv)
  -f FORMAT, --format FORMAT
                        Output file format. (available options default and
                        libra)
  -s START_DATE, --start-date START_DATE
                        Start date of the requested date range in YYYY-MM-DD
                        format. (default = 2010-01-01)
  -e END_DATE, --end-date END_DATE
                        End date of the requested date range in YYYY-MM-DD
                        format. (default = 2020-01-01)

usage: weight_exporter.py [-h] [-o OUTPUT_FILE] [-f FORMAT] [-s START_DATE]
                          [-e END_DATE]

Sample usage:

  $ python weight-exporter.py -s 2017-12-01 -e 2018-03-20
'''

import sys
import argparse
import csv
import importlib

from datetime import datetime

import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

import weight_formatter

ARGPARSER = argparse.ArgumentParser(
    description=
    'Reads weight data from Google Fitness API and export to a CSV file')
ARGPARSER.add_argument(
    '-o',
    '--output-file',
    type=str,
    help=('Output file path. (default = google-fit-weight-XXX.csv)'),
    default='google-fit-weight-' + datetime.now().strftime('%s') + '.csv')
ARGPARSER.add_argument(
    '-f',
    '--format',
    type=str,
    help=('Output file format. (available options default and libra)'),
    default='libra')
ARGPARSER.add_argument('-s',
                       '--start-date',
                       type=str,
                       help=('Start date of the requested date range in '
                             'YYYY-MM-DD format. (default = 2010-01-01)'),
                       default='2010-01-01')
ARGPARSER.add_argument('-e',
                       '--end-date',
                       type=str,
                       help=('End date of the requested date range in '
                             'YYYY-MM-DD format. (default = 2020-01-01)'),
                       default='2020-01-01')

def get_authenticated_service():
  flow = InstalledAppFlow.from_client_secrets_file(
      "client_secret.json", 'https://www.googleapis.com/auth/fitness.body.read')

  credentials = flow.run_local_server(
      host='localhost',
      port=8080,
      authorization_prompt_message='Please visit this URL: {url}',
      success_message='The auth flow is complete; you may close this window.',
      open_browser=True)
  return build('fitness', 'v1', credentials=credentials)


def main(argv):
  argparsed = ARGPARSER.parse_args(argv[1:])
  formatter = getattr(weight_formatter,
                      argparsed.format + "_formatter")(argparsed.output_file)

  try:
    start_date = datetime.strptime(argparsed.start_date.strip(), '%Y-%m-%d')
    end_date = datetime.strptime(argparsed.end_date.strip(), '%Y-%m-%d')
  except:
    ARGPARSER.print_help()
    exit(-1)

  print(
      'Export values between %s and %s\n' %
      (start_date.strftime('%a, %d %b %Y'), end_date.strftime('%a, %d %b %Y')))

  print('Creating API Service')
  service = get_authenticated_service()

  print('Fetching Google Fit Weight Data Sources')
  datasources = service.users().dataSources().list(
      userId='me', dataTypeName='com.google.weight').execute()

  print('Fetching Google Fit Weight Dataset')
  dataset = service.users().dataSources().datasets().get(
      userId='me',
      dataSourceId=
      'derived:com.google.weight:com.google.android.gms:merge_weight',
      datasetId=to_nano_epoch(start_date) + '-' +
      to_nano_epoch(end_date)).execute()

  line_count = 0

  print('Exporting Google Fit Weight Dataset (expected %d row)' %
        len(dataset['point']))

  formatter.write_header()

  for point in dataset['point']:
    out_data = json_to_row(datasources, point)
    line_count += 1
    formatter.write_weight(out_data)
  formatter.write_footer()

  print('\nTotal %d value extracted to %s' %
        (line_count, argparsed.output_file))


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
      'Second': point_date.second
  }
  return out_data


def data_source_name(datasources, datastreamid):
  ds = (s for s in datasources['dataSource']
        if s['dataStreamId'] == datastreamid).__next__()
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
