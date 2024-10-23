#!/usr/bin/env python3

import argparse
import codecs
import lxml.etree as et
import os
import re
import sys
from palaso.langtags import LangTag
from pathlib import Path

try:
    from oxttools.xmltemplate import Templater
except ImportError:
    sys.path.append(str(Path(__file__).parents[1] / 'lib'))
    # sys.path.append(os.path.join(os.path.dirname(__file__), '..','lib'))
    from oxttools.xmltemplate import Templater


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'infile',
        help='xml file to process'
    )
    parser.add_argument(
        'outfile',
        help='Ouptut file to generate'
    )
    parser.add_argument(
        '-t',
        '--template',
        help='Template file to generate from'
    )
    parser.add_argument(
        '-l',
        '--langtag',
        help='Maximal Langtag for this data'
    )
    args = parser.parse_args()
    t = Templater()
    datadir = str(Path(__file__).parents[1] / 'lib' / 'oxttools' / 'data')
    # datadir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../lib/oxttools/data"))  # noqa: E501
    if args.template is None:
        args.template = str(Path(datadir) / 'simple_ldml.fodt')
        # args.template = os.path.join(datadir, 'simple_ldml.fodt')
    t.define('resdir', datadir)
    t.define('repdir', os.path.abspath(os.path.dirname(args.template)))

    if args.langtag is None:
        lt = re.sub(
            r"^([a-zA-Z_\-]+).xml",
            r"\1", os.path.basename(args.infile)
        )
        if "." not in lt:
            ltag = LangTag(lt)
            args.langtag = ltag.analyse()
    else:
        ltag = LangTag(args.langtag)
        args.langtag = ltag.analyse()

    if args.langtag is not None:
        ltag = LangTag(args.langtag)
        args.langtag = ltag.analyse()
        t.define('lang', args.langtag.lang)
        t.define('script', args.langtag.script)
        if args.langtag.script:
            t.define('lscript', args.langtag.script.lower())
        t.define('region', args.langtag.region)
        # print t.vars

    t.parse(args.template)
    oldd = et.parse(args.infile).getroot()
    nsmap = oldd.nsmap
    nsmap['sil'] = 'urn://www.sil.org/ldml/0.1'
    d = et.Element(oldd.tag, nsmap=nsmap)
    d[:] = oldd[:]
    if args.template.endswith('.fodt'):
        t.processodt(context=d)
    else:
        t.process(context=d)
    with codecs.open(args.outfile, "w", encoding="utf-8") as of:
        of.write("<?xml version='1.0'?>\n")
        of.write(str(t))


if __name__ == '__main__':
    main()
