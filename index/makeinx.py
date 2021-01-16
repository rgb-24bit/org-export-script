# -*- coding: utf-8 -*-

"""
Generate the index based on the org file in the directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2021 by rgb-24bit.
:license: MIT, see LICENSE for more details.
"""

from __future__ import annotations

import os
import re

from pathlib import Path
from typing import TextIO, List


class Node:
    _org_title_matcher = re.compile(r'#\+TITLE:\s*(.+)')
    _org_suffix        = '.org'

    def  __init__(self, path: Path):
        self._path    = path
        self._name    = None
        self._suborgs = []
        self._subdirs = []

        if self._path.is_dir():
            self._walk()

    @property
    def name(self) -> str:
        if self.is_dir():
            return self._path.name

        with open(self._path, encoding='utf-8') as fp:
            match = self._org_title_matcher.search(fp.readline())
            if match: return match.group(1)

        return self._path.stem

    @property
    def path(self) -> str:
        return self._path.as_posix()

    @property
    def suborgs(self) -> List[Node]:
        return self._suborgs

    @property
    def subdirs(self) -> List[Node]:
        return self._subdirs

    def is_dir(self) -> bool:
        return self._path.is_dir()

    def _walk(self):
        # Need sorted directories and files
        for subitem in sorted(os.listdir(self._path)):
            subnode = Node(Path(self._path, subitem))
            if subnode.is_dir():
                if len(subnode._subdirs) > 0 or len(subnode._suborgs) > 0:
                    self._subdirs.append(subnode)
            elif subnode._path.suffix == self._org_suffix:
                self._suborgs.append(subnode)


def make_index_format_md(root: Node, fd: TextIO):
    def make_catalog():
        fd.write('## Table of contents\n')
        itemfmt = '  + [{name}](#{anchor})\n'
        for item in root.subdirs:
            fd.write(itemfmt.format(name=item.name, anchor=item.name.lower()))

    def make_index(node: Node, level: int = 0):
        headfmt = '## {name}\n'
        typefmt = '  ' * level + '+ **{name}**\n'
        itemfmt = '  ' * level + '+ [{name}]({href})\n'

        for subdir in node.subdirs:
            if level == 0:
                fd.write(headfmt.format(name=subdir.name))
            else:
                fd.write(typefmt.format(name=subdir.name))
            make_index(subdir,  level + 1)

        for suborg in node.suborgs:
            fd.write(itemfmt.format(name=suborg.name,
                                    href=suborg.path))
    make_catalog()
    make_index(root)


def make_index_format_org(root: Node, fd: TextIO):
    def make_index(node: Node, level: int = 0):
        headfmt = '* {name}\n'
        typefmt = '  ' * level + '+ *{name}*\n'
        itemfmt = '  ' * level + '+ [[file:{href}][{name}]]\n'

        for subdir in node.subdirs:
            if level == 0:
                fd.write(headfmt.format(name=subdir.name))
            else:
                fd.write(typefmt.format(name=subdir.name))
            make_index(subdir,  level + 1)

        for suborg in node.suborgs:
            fd.write(itemfmt.format(name=suborg.name,
                                    href=suborg.path))
    make_index(root)


def make(fn: str, basedir: str, fmt: str):
    with open(fn, 'w', encoding='utf-8') as fd:
        if fmt == 'md':
            make_index_format_md(Node(basedir), fd)
        else:
            make_index_format_org(Node(basedir), fd)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Make org file index power by python.')

    parser.add_argument('--base', required=True, type=Path)
    parser.add_argument('--name', required=True)
    parser.add_argument('--fmt', required=True)

    args = parser.parse_args()

    make(args.name, args.base, args.fmt)
