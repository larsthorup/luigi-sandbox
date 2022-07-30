# luigi-sandbox

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
python -m luigi --module frequency GetTopBooks
python -m luigi --module frequency DownloadBooks --FileID 2
```
