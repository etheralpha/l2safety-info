# l2safety-info

This is the source code for <https://l2safety.info>.

## Local Development

1. Clone the repo (or fork the repo to your account)
1. Install dependencies: `bundle install`
1. Create a feature branch off of the `main` branch
1. Start the local server: `bundle exec jekyll serve`
1. Go to <http://localhost:4400/> to view changes

To build the site use `bundle exec jekyll build`.

Resources:

- [Jekyll Docs](https://jekyllrb.com/docs/)
- [Liquid Syntax](https://shopify.github.io/liquid/basics/introduction/)


## Scripts

To run the script in `_script`:
1. Create virtual environment: `python3 -m venv _scripts/venv/`
1. Start the local server: `. _scripts/venv/bin/activate && pip install -r _scripts/requirements.txt && python _scripts/collect_data.py`
1. Or run each command individually:
    1. Start python virtual environment: `. _scripts/venv/bin/activate`
    1. Install dependencies: `pip install -r _scripts/requirements.txt`
    1. Run the script: `python _scripts/collect_data.py`
1. Close virtual environment: `deactivate`


