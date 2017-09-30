# netwatch

A collection of tools to watch for new content on the Internet.

* RSS/Atom feeds
* Twitter feeds
* URLs on webpages (work in progress)
* Mailbox rendering (work in progress)

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
    venv/bin/netwatch feeds.yml 2>>log | bin/pegasus-publish

Mailboxes can also be watched (work in progress) and rendered to HTML:

    #!/bin/sh
    cd $HOME/code/netwatch/
    venv/bin/python bin/watchbox user:pass@imap-server /var/www/mails/ http://example.com/mails/ 2>>log | bin/pegasus-publish '#mychannel'

The `pegasus-publish` script is just an example: in this case it outputs
messages over a UNIX socket to an IRC bot.


## Session data

Netwatch stores its session data on disk as JSON object:

* The scheduled next attempt
* Recently seen items (to determine which items are new)
* Cache-related headers, such as Last-Modified/E-Tag

Each feed has a unique name associated with it which is used to determine the
path on disk for the session object. The default path is '.session' in the
current working directory.


## TODO

- Different schedules for just-had-update and no-updates
    - Store entry time vs fetched time
- Error monitoring
- Webpage export?
