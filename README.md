# opsmanager-snapshots-retriever
## Configuration file
- `base_url`: URL of Ops/Cloud Manager
- `username`: User name used to access Ops/Could Manager
- `api_key`: API Key used to access Ops/Could Manager
- `log_level`: Standard Python log levels. INFO/DEBUG...
- `output_file`: Output file path. Includ `{0}` to add timestamp. e.g.: `./output-{0}.json`

## Python version
This script respects pyenv settings. You can add Python version to `.python-version`

## Usage
```
python __main__.py
```
