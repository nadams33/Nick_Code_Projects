# Nova Calculator

A FastAPI-powered calculator with a responsive static interface.

## Run locally

```bash
python -m pip install -r requirements.txt
uvicorn print_hi_nick:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Calculation API

Send a JSON expression to `POST /calc`:

```bash
curl -X POST http://127.0.0.1:8000/calc \
  -H "Content-Type: application/json" \
  -d '{"expression":"(12 + 8) * 2"}'
```

The response contains the original expression and numeric result:

```json
{"expression":"(12 + 8) * 2","result":40}
```

Supported operators are `+`, `-`, `*`, `/`, `//`, `%`, and `**`.
