# netwatch

A collection of tools to watch for new content on the Internet.

* RSS/Atom feeds
* Twitter feeds
* URLs on webpages (work in progress)

New content updates are sent as single-line JSON blobs, which can then be
further processed by the tool of your choosing.


## Getting started

Install the package and its dependencies. A virtual environment is well suited
for this:

    virtualenv -p python3 venv
    venv/bin/pip install -e .


## Usage example

A simple cron-style usage example:

    #!/bin/sh
    cd $HOME/code/netwatch/
    venv/bin/netwatch --session-data .fc feeds.yml 2>>log | bin/pegasus-publish


## TODO

- Fix some of the hardcoded paths/defaults
- Tool to inspect cache/view scheduled times
- Error monitoring
- Mail?
- Webpage export?
