# Visualisation tool for parcel delivery algorithm

## Frontend
### Requirements
- nodejs
- npm
- yarn

### Install
```
cd frontend
yarn install
```

### Run
```
yarn serve
```

## Backend

### Requirements
- Python 3.6+
- Virtualenv
- Pip

### Install
```
conda config --prepend channels conda-forge
conda create -n cenv --strict-channel-priority osmnx

### Activate the environment ###

pip install -r requirements.txt
```


### Run backend application
```
python application/main.py
```

### Run backend tests
```
pytest
```

### Docker
cd to the root of this project.
```
Docker build . 
```
To easily find your image you could tag your Docker image:
```
Docker build . -t almende/visualisation
```

After the image is built, you can run a container by doing:
```
Docker run -p 8080:80 <tag>
```
<tag> is either the tag you specified, or a random UID created by Docker 
if you did not specify a tag yourself.