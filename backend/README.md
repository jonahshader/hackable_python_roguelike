# Setup

## Install conda

[miniconda](https://docs.anaconda.com/miniconda/)

## Create conda env from environment.yml

Make sure you are in the backend directory, then run:

```bash
conda env create -f environment.yml
```

This create a conda env named rogue.

## Activate conda env

```bash
conda activate rogue
```

or use the GUI in VSCode or PyCharm.


## Running the server (FastAPI)

Make sure you are in the backend directory, then run:

```bash
fastapi dev .\src\main.py
```
or
```bash
uvicorn src.main:app --reload
```
