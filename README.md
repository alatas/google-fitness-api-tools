# Google Fit(ness) Api Tools
Google Fit and some other fitness oriented apps read and write Google Fitness Data Store. These mini tools can import, export and manipulate these data. To access your fitness data, authorization may be needed. Tools could open an authorization window and ask for grant access to your fitness data.

## Prerequisities
The tools need the Python client library for Google APIs. To install the library, use `pip` or `easy_install`:

```bash
$ pip install --upgrade google-api-python-client
```
or
```bash
$ easy_install --upgrade google-api-python-client
```

## Install
```bash
git clone https://github.com/alatas/google-fitness-api-tools.git
```

## Tools
### [Weight Exporter](weight_export.md)
Reads weight data from Google Fitness API and export to a CSV file