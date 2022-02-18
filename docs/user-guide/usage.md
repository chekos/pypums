# How to use `PyPUMS`

You can use `pypums` as a CLI on your terminal or in your scripts or notebooks.

## As a CLI

On your terminal `pypums --help` or `pypums --version` to make sure it's installed 

```shell
pypums --version
>>> pypums v0.1
```

The `pypums` CLI has 2 commands `acs-url` and `download-acs`.

### `pypums acs-url`
The `acs-url` command will return the URL pointing to the zip file in the Census server containing the data you're looking for. It takes in _at least_ two arguments: `year` and `state`.

```shell
pypums acs-url --year 2018 --state california
>>>> https://www2.census.gov/programs-surveys/acs/data/pums/2018/1-Year/csv_pca.zip
```

Use `pypums acs-url --help` for more information.
```plaintext
Usage: pypums acs-url [OPTIONS]

  Builds URL pointing to the Census Bureau's FTP server
  containing the data for the desired ACS.

Options:
  --year INTEGER      Year of survey (2000 - 2019)  [required]
  --state TEXT        One of the 50 US States or District of
                      Columbia  [required]
  --survey TEXT       One of '1-', '3-' or '5-year'  [default:
                      1-year]
  --sample-unit TEXT  Unit of observation (person or household)
                      [default: person]
  --help              Show this message and exit.
```

### `pypums download-acs`
You can use the `download-acs` command to download the zip file containing the data for the specified ACS. It will extract it by default. 

This command requires at least the `year` and `state` of the survey to download.

```shell
pypums download-acs --year 2018 --state california
```

Use `pypums download-acs --help` for more information.
```plaintext
Usage: pypums download-acs [OPTIONS]

  Downloads and, optionally, extracts data related to the
  specified ACS into a specified directory.

Options:
  --year INTEGER                  Year of survey (2000 - 2019)
                                  [required]
  --state TEXT                    One of the 50 US States or
                                  District of Columbia
                                  [required]
  --survey TEXT                   One of '1-', '3-' or '5-year'
                                  [default: 1-year]
  --sample-unit TEXT              Unit of observation (person or
                                  household)  [default: person]
  --data-directory DIRECTORY      [default: ~/Libr
                                  ary/Application
                                  Support/pypums/data]
  -e, --extract                   Extract the downloaded zip
                                  file?  [default: True]
  --overwrite-download / --no-overwrite-download
                                  Overwrite previously
                                  downloaded version of this
                                  data  [default: no-overwrite-
                                  download]
  --overwrite-extract / --no-overwrite-extract
                                  Overwrite previously extracted
                                  version of this data
                                  [default: no-overwrite-
                                  extract]
  --help                          Show this message and exit.
```