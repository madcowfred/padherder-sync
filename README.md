padherder-sync
==============

Simple script to sync JSON box data via the PADherder API

WARNING
-------
BACK UP YOUR PADHERDER DATA (username dropdown, 'Export to CSV') in case something goes horribly wrong, I have only tested this with a small set of sample data.

Requirements
------------

- A [PADHerder](https://www.padherder.com) account
- A dump of your JSON box data from somewhere

#### Windows
- Use the latest zip file from downloads, it includes a pre-built binary.

#### Not-Windows
- [Python 2.6/2.7](http://www.python.org)
- [Requests](http://docs.python-requests.org/en/latest/) - `pip install requests`

Usage
-----

#### Windows
`padherder_sync.exe [capture file] [PADherder username] [PADherder password]`

#### Not-Windows
`python padherder_sync.py [capture file] [PADherder username] [PADherder password]`
