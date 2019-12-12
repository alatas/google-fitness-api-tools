import csv


class default_formatter():

  def __init__(self, output_file):
    super().__init__()
    fields = [
        'Source', 'Value(kg)', 'Date', 'Year', 'Month', 'Day', 'Hour', 'Minute',
        'Second'
    ]

    self._file = open(output_file, 'w')
    self._writer = csv.DictWriter(self._file, fieldnames=fields, delimiter='\t')

  def write_header(self):
    self._writer.writeheader()

  def write_footer(self):
    self._file.close()
    pass

  def write_weight(self, out_data):
    self._writer.writerow(out_data)


class libra_formatter():
  #Version:5
  #Units:kg

  #date;weight;weight trend;body fat;body fat trend;comment
  #2019-06-11 09:49:00;138.4;138.4;;;
  def __init__(self, output_file):
    super().__init__()
    fields = [
        'Date', 'Value(kg)', 'weight trend', 'body fat', 'body fat trend',
        'comment'
    ]

    self._file = open(output_file, 'w')
    self._writer = csv.DictWriter(self._file,
                                  fieldnames=fields,
                                  delimiter=';',
                                  extrasaction='ignore')

  def write_header(self):
    self._file.writelines([
        '#Version:5\n', '#Units:kg\n', '\n',
        '#date;weight;weight trend;body fat;body fat trend;comment\n'
    ])

  def write_footer(self):
    self._file.close()
    pass

  def write_weight(self, out_data):
    out_data['weight trend'] = ''
    out_data['body fat'] = ''
    out_data['body fat trend'] = ''
    out_data['comment'] = ''
    out_data['Date'] = out_data['Date'].replace('T', ' ')
    self._writer.writerow(out_data)