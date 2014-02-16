padherder-sync
==============

Simple script to sync JSON box data via the PADherder API

WARNING
-------
BACK UP YOUR PADHERDER DATA (username dropdown, 'Export to CSV') in case something goes horribly wrong, I have only tested this with a small set of sample data.

Requirements
------------
- [Python 2.6/2.7](http://www.python.org)
- [Requests](http://docs.python-requests.org/en/latest/) - `pip install requests`
- A [PADHerder](https://www.padherder.com) account
- A dump of your JSON box data from somewhere

Usage
-----
`python padherder_sync.py [capture file] [PADherder username] [PADherder password]`
