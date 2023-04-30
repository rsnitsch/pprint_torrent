#!/usr/bin/env python3
"""
Small tool to pretty-print the structure of a torrent file.

The binary pieces data is hidden and the piece root hashes are hexlified.
"""
import argparse
import binascii
from copy import deepcopy
from pathlib import Path
from pprint import pformat
from typing import Dict, Any, Union, Optional

from bencodepy import decode, encode

__version__ = '1.0.0'


def hexlify_piece_roots(file_tree: Dict[bytes, Any]) -> Dict[bytes, Any]:
    """Recursively hexlify all piece roots binary data in the given file tree dict."""
    if b'pieces root' in file_tree:
        file_tree[b'pieces root'] = binascii.hexlify(file_tree[b'pieces root'])
    else:
        for key in file_tree.keys():
            file_tree[key] = hexlify_piece_roots(file_tree[key])
    return file_tree


def pformat_torrent(metainfo: Dict[bytes, Any],
                    indent: int = 2,
                    width: int = 200,
                    depth: Optional[int] = None,
                    copy: bool = True) -> str:
    """
    Pretty prints the given metainfo dict into a string. Binary data is hidden. Piece root hashes are hexlified.

    @param metainfo: The metainfo dict to pretty-print
    @param indent: The indentation width, gets passed to pprint.pformat internally.
    @param width: The maximum width of a line, gets passed to pprint.pformat internally.
    @param depth: The maximum depth to show, gets passed to pprint.pformat internally.
    @param copy: If False, the metainfo dict will be modified inplace (by reference) before pretty-printing. Modifications include
                 hiding binary data and hexlifying piece root hashes. If True, the metainfo dict will be deep-copied
                 before applying these changes so that the caller's copy of metainfo will not be affected.
    """
    if copy:
        metainfo = deepcopy(metainfo)

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

    return pformat(metainfo, indent, width, depth)


def pprint_torrent(metainfo: Dict[bytes, Any],
                   indent: int = 2,
                   width: int = 200,
                   depth: Optional[int] = None,
                   copy: bool = True) -> None:
    """Do the same as pformat_torrent but print to stdout directly."""
    print(pformat_torrent(metainfo, indent, width, depth, copy=copy))


def load_torrent(path: Union[Path, str]) -> Dict[bytes, Any]:
    """Load a torrent file from the given path and return the metainfo dict."""
    if not isinstance(path, Path):
        if not isinstance(path, str):
            raise ValueError('path must be a str or Path object')
        path = Path(path)

    with path.open('rb') as fh:
        metainfo = decode(fh.read())

    if not isinstance(metainfo, dict):
        raise ValueError('Invalid torrent data: Does not contain a metainfo dict')

    return metainfo


def save_torrent(path: Union[Path, str], metainfo: Dict[bytes, Any]) -> None:
    """Save the given metainfo dict as a torrent file to the given path."""
    if not isinstance(path, Path):
        if not isinstance(path, str):
            raise ValueError('path must be a str or Path object')
        path = Path(path)

    with path.open('wb') as fh:
        fh.write(encode(metainfo))


def main() -> None:
    """Pretty-print a given torrent file to stdout."""
    parser = argparse.ArgumentParser(description='Pretty-print a given torrent file\'s metainfo dict to stdout.',
                                     epilog='Version: %s' % __version__)
    parser.add_argument('torrent_file', type=Path, help='Path to the torrent file')
    parser.add_argument('-i', '--indent', type=int, default=2, help='Indentation width (default: 2)')
    parser.add_argument('-w', '--width', type=int, default=200, help='Maximum width of a line (default: 200)')
    parser.add_argument('-d', '--depth', type=int, default=None, help='Maximum depth to show (default: unlimited)')
    args = parser.parse_args()

    if not args.torrent_file.is_file():
        print('Error: The specified torrent file does not exist')
        return

    metainfo = load_torrent(args.torrent_file)
    pprint_torrent(metainfo, args.indent, args.width, args.depth, copy=False)


if __name__ == '__main__':
    main()
