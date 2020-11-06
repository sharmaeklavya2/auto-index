#!/usr/bin/env python3

"""Recursively generate an HTML index page for each directory."""

from __future__ import print_function

import os
from os.path import join as pjoin
import stat
import json
import argparse
from base64 import b64encode

IGNORES = set("""
.git
.gitignore
__pycache__
index.html
Thumbs.db
Desktop.ini
.DS_Store
""".split())

IGNORE_EXTS = set("""
.pyc
.swp
.swo
""".split())

ICON_MIME_TYPE = {
    ".svg": "image/svg+xml",
    ".png": "image/png",
}

STYLE_FILE_NAME = 'index-style.css'
IGNORES.add(STYLE_FILE_NAME)
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('dirpath')
parser.add_argument('--template')
parser.add_argument('--style')
parser.add_argument('--internal-style', dest='external_style',
    action='store_false', default=True)
parser.add_argument('--icons-dir')
args = parser.parse_args(None if __name__ == '__main__' else [])

if args.template is None:
    args.template = pjoin(SCRIPT_DIR, 'template.html')
if args.icons_dir is None:
    args.icons_dir = pjoin(SCRIPT_DIR, 'icons')
if args.style is None:
    args.style = pjoin(SCRIPT_DIR, 'style.css')


class Resources:
    page_template = None
    style_template = None
    icons = None
    ext_to_type = None

    @staticmethod
    def update(template_path, icons_dir, style_path):
        if Resources.page_template is None:
            import jinja2
            with open(template_path) as fp:
                Resources.page_template = jinja2.Template(fp.read())
        if Resources.icons is None:
            Resources.icons = {}
            for entry in os.scandir(icons_dir):
                if not entry.is_dir():
                    name, ext = os.path.splitext(entry.name)
                    with open(entry.path, 'rb') as fp:
                        if ext in ICON_MIME_TYPE:
                            Resources.icons[name] = 'data:{};base64,{}'.format(ICON_MIME_TYPE[ext],
                                b64encode(fp.read()).decode('ascii'))
        if Resources.ext_to_type is None:
            with open(pjoin(SCRIPT_DIR, 'ext_map.json')) as fp:
                data = json.load(fp)
            Resources.ext_to_type = {}
            for ftype, exts in data.items():
                for ext in exts:
                    Resources.ext_to_type[ext] = ftype
        if Resources.style_template is None:
            with open(style_path) as fp:
                Resources.style_template = jinja2.Template(fp.read().strip())


ftypes_seen = set()


def get_file_type(root, name, is_dir):
    if is_dir:
        ftype = 'dir'
    else:
        name, ext = os.path.splitext(name)
        ftype = Resources.ext_to_type.get(ext[1:], 'file')
    ftypes_seen.add(ftype)
    return ftype


def get_link_target(root, name, is_dir):
    return None


def minify(s):
    stripped_lines = [line.strip() for line in s.split('\n')]
    return '\n'.join([line for line in stripped_lines if line]) + '\n'


def generate_index(root, dnames, fnames, depth):
    base_root = os.path.relpath(root, args.dirpath)
    items = []
    for dname in dnames:
        items.append((dname, get_file_type(root, dname, True),
            get_link_target(root, dname, True)))
    for fname in fnames:
        items.append((fname, get_file_type(root, fname, False),
            get_link_target(root, fname, False)))
    ftypes = {ftype for name, ftype, target in items}

    icons2 = {k: v for k, v in Resources.icons.items() if k in ftypes}
    if args.external_style:
        style = '<link rel="stylesheet" href="{}{}" />'.format('../' * depth, STYLE_FILE_NAME)
    else:
        style = '<style>\n{}\n</style>'.format(Resources.style_template.render({'icons': icons2}))
    page = Resources.page_template.render({
        'root': '/' + ('' if base_root == '.' else base_root),
        'items': items,
        'icons': icons2,
        'style': style,
    })
    with open(pjoin(root, 'index.html'), 'w') as fp:
        fp.write(minify(page))


def index_walk(root, depth=0):
    fnames, dnames, all_dnames = [], [], []
    found_noindex = False
    for entry in os.scandir(root):
        if entry.name not in IGNORES and os.path.splitext(entry.name)[1] not in IGNORE_EXTS:
            if entry.name == '.noindex':
                found_noindex = True
            if entry.is_dir():
                all_dnames.append(entry.name)
            if entry.stat().st_mode & stat.S_IROTH:
                if entry.is_dir():
                    dnames.append(entry.name)
                elif entry.is_file():
                    fnames.append(entry.name)
                else:
                    raise Exception('Strange file: {}'.format(entry.path))
    if not found_noindex:
        generate_index(root, sorted(dnames), sorted(fnames), depth)
    for dname in all_dnames:
        index_walk(pjoin(root, dname), depth + 1)


def main():
    Resources.update(args.template, args.icons_dir, args.style)
    index_walk(args.dirpath)
    if args.external_style:
        icons2 = {k: v for k, v in Resources.icons.items() if k in ftypes_seen}
        style = Resources.style_template.render({'icons': icons2})
        with open(pjoin(args.dirpath, STYLE_FILE_NAME), 'w') as fp:
            fp.write(style)


if __name__ == '__main__':
    main()
