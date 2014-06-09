MadeData
========

A simple tool for listing the contents of public S3 buckets.

### Installation

The dependencies for this project are located within the requirements.txt file.
You can install them using ``pip`` like so:

``` bash
$ pip install -r requirements.txt
```

### Configuration

This application looks two environmental variables ``AWS_ACCESS_KEY`` and
``AWS_SECRET_KEY`` to allow it to connect to Amazon Web Services and figure out
what you have stored in your publicly available buckets. 

### Running the app

To run the application locally, do this:

```bash
$ python app.py
```

This will run a development server on port 9999. 

## Team

* Derek Eder - developer, content
* Eric van Zanten - developer, GIS data merging

## Errors / Bugs

If something is not behaving intuitively, it is a bug, and should be reported.
Report it here: https://github.com/datamade/madedata/issues

## Note on Patches/Pull Requests
 
* Fork the project.
* Make your feature addition or bug fix.
* Commit, do not mess with rakefile, version, or history.
* Send me a pull request. Bonus points for topic branches.

## Copyright

Copyright (c) 2014 DataMade Released under the [MIT
License](https://github.com/datamade/madedata/blob/master/LICENSE).

