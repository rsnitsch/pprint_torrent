#!/usr/bin/env python3
"""
Small tool to pretty-print the structure of a torrent file.

The binary pieces data is hidden and the piece root hashes are hexlified.
"""
import argparse
import binascii
from pathlib import Path
from pprint import pformat
from typing import Dict, Any

from bencodepy import decode


def hexlify_piece_roots(file_tree: Dict[bytes, Any]) -> Dict[bytes, Any]:
    """Recursively hexlify all piece roots binary data in the given file tree dict."""
    if b'pieces root' in file_tree:
        file_tree[b'pieces root'] = binascii.hexlify(file_tree[b'pieces root'])
    else:
        for key in file_tree.keys():
            file_tree[key] = hexlify_piece_roots(file_tree[key])
    return file_tree


def pformat_torrent(metainfo: Dict[bytes, Any], *args: int, **kwargs: bool) -> str:
    """
    Pretty prints the given metainfo dict into a string. Binary data is hidden. Piece root hashes are hexlified.

    args and kwargs are passed to Python's pprint.pformat.
    """
    if not b'info' in metainfo:
        raise ValueError('Invalid metainfo dict: Missing "info" key')

    if b'pieces' in metainfo[b'info']:
        metainfo[b'info'][b'pieces'] = '%d bytes (hidden in this output)' % len(metainfo[b'info'][b'pieces'])
    if b'piece layers' in metainfo:
        keys = list(metainfo[b'piece layers'].keys())
        for key in keys:
            metainfo[b'piece layers'][binascii.hexlify(key)] = '%d bytes (hidden in this output)' % len(
                metainfo[b'piece layers'][key])
            del metainfo[b'piece layers'][key]
    if b'file tree' in metainfo[b'info']:
        metainfo[b'info'][b'file tree'] = hexlify_piece_roots(metainfo[b'info'][b'file tree'])

    return pformat(metainfo, *args, **kwargs)


def pprint_torrent(metainfo: Dict[bytes, Any], *args: int, **kwargs: bool) -> None:
    """Do the same as pformat_torrent but print to stdout directly."""
    print(pformat_torrent(metainfo, *args, **kwargs))


def main() -> None:
    """Pretty-print a given torrent file to stdout."""
    parser = argparse.ArgumentParser(description='Pretty-print a given torrent file\'s metainfo dict to stdout.')
    parser.add_argument('torrent_file', type=Path, help='Path to the torrent file')
    parser.add_argument('-i', '--indent', type=int, default=2, help='Indentation width (default: 2)')
    parser.add_argument('-w', '--width', type=int, default=200, help='Maximum width of a line (default: 200)')
    parser.add_argument('-d', '--depth', type=int, default=None, help='Maximum depth to show (default: unlimited)')
    args = parser.parse_args()

    if not args.torrent_file.is_file():
        print('Error: The specified torrent file does not exist')
        return

    with args.torrent_file.open('rb') as fh:
        metainfo = decode(fh.read())

    pprint_torrent(metainfo, args.indent, args.width, args.depth)


if __name__ == '__main__':
    main()
