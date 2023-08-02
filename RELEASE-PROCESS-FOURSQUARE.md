## Publishing new versions of our internal fork

### Building the wheel
```
python3.9 -m venv venv
source venv/bin/activate
python -m pip install -U pip
python -m pip install build
python -m build --wheel --outdir dist
deactivate
```

### Publishing
```
source venv/bin/activate
python -m pip install twine
```
And then follow the steps described in [this](https://foursquare.atlassian.net/wiki/spaces/FE/pages/3702226964/Publishing+pips+to+Artifactory) document.
