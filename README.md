# pprint_torrent

Pretty-print the contents of torrent files!

pprint_torrent can be used to inspect the contents of torrent files. The metainfo dict is pretty-printed
with indendation of sub-levels. The maximum depth can be limited as well. To keep the output compact, the long
binary `pieces` hash sequence is hidden from the output automatically. `pieces root` hashes from v2 torrents are
hexlified (both in the `file tree` and in the `piece layers` dict).

## Usage

Commandline parameters:

    usage: pprint_torrent.py [-h] [-i INDENT] [-w WIDTH] [-d DEPTH] torrent_file

    Pretty-print a given torrent file's metainfo dict to stdout.

    positional arguments:
    torrent_file          Path to the torrent file

    options:
    -h, --help            show this help message and exit
    -i INDENT, --indent INDENT
                            Indentation width (default: 2)
    -w WIDTH, --width WIDTH
                            Maximum width of a line (default: 200)
    -d DEPTH, --depth DEPTH
                            Maximum depth to show (default: unlimited)

Example command:

    $ pprint_torrent.py kubuntu-20.04-desktop-amd64.iso.torrent -w 100

Output:

    { b'announce': b'https://torrent.ubuntu.com/announce',
      b'comment': b'Kubuntu CD cdimage.ubuntu.com',
      b'creation date': 1587648815,
      b'info': { b'length': 2354036736,
                 b'name': b'kubuntu-20.04-desktop-amd64.iso',
                 b'piece length': 1048576,
                 b'pieces': '44900 bytes (hidden in this output)'}}

## Installation

Execute:

    pip install pprint_torrent
