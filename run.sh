export PYTHONPATH="$HOME/dev/github/ref-cisis-doc"
source $PYTHONPATH/venv/bin/activate
python main.py --config=default/config.json --sync --ftpconfig=myconf/ftp-data.json