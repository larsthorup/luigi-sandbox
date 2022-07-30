# luigi-sandbox

https://www.digitalocean.com/community/tutorials/how-to-build-a-data-processing-pipeline-using-luigi-in-python-on-ubuntu-20-04

## setup

```
python -m venv venv
. venv/Scripts/activate
python -m pip install -r requirements.txt
```

## hello

```
python -m luigi --module hello HelloLuigi --local-scheduler
```

## luigi scheduler

```
luigid --port 8082
```

## luigi dashboard

- http://localhost:8082

## frequency

```
python -m luigi --module frequency TopWords --GlobalParams-NumberBooks 15 --GlobalParams-NumberTopWords 750
```
