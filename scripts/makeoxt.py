#!/usr/bin/env python3

import codecs
import os
import sys
import time
import unicodedata
from pathlib import Path
try:
    import oxttools.xmltemplate as xtmpl
except ImportError:
    sys.path.append(str(Path(__file__).parents[1] / 'lib'))
    import oxttools.xmltemplate as xtmpl
import oxttools.hunspell as hs
from argparse import ArgumentParser
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import lxml.etree as et

langres = (
    "af-ZA", "ak-GH", "am-ET", "an-ES", "apt-IN", "arn-CL", "as-IN",
    "ast-ES", "axk-CF", "av-RU", "az-AZ", "ba-RU", "be-BY", "beq-CG", "bg-BG",
    "bin-NG", "bkw-CG", "bm-ML", "bn-BD", "bo-CN", "br-FR", "brx-IN", "buc-YT",
    "bvx-CG", "ca-ES", "chr-US", "co-FR", "cop-EG", "cs-CZ", "csb-PL", "cu-RU",
    "cv-RU", "cy-GB", "da-DK", "dde-CG", "de-DE", "dgo-IN", "dv-MV", "ebo-CG",
    "ee-GH", "el-GR", "es-ES", "et-EE", "fa-IR", "ff-SN", "fi-FI", "fil-PH",
    "fj-FJ", "fkv-NO", "frp-FR", "fo-FO", "fon-BJ", "fur-IT", "fuv-NG",
    "fy-NL", "ga-IE", "gd-GB", "gl-ES", "grc-GR", "gsc-FR", "gsw-FR", "gu-IN",
    "gug-PY", "gv-GB", "gym-PA", "ha-NG", "haw-US", "he-IL", "hi-IN", "hil-PH",
    "hr-HR", "hsb-DE", "ht-HT", "hu-HU", "hy-AM", "ibb-NG", "id-ID", "ig-NG",
    "ii-CN", "is-IS", "it-IT", "iyx-CG", "ja-JP", "ka-GE", "kab-DZ", "kca-RU",
    "ki-KE", "kk-KZ", "kkw-CG", "kl-GL", "km-KH", "kn-IN", "kng-CD", "ko-KR",
    "koi-RU", "kok-IN", "kpv_RU", "kr-NG", "ksf-CM", "ktu-CD", "kum-RU",
    "kw-UK", "ky-KG", "lb-LU", "ldi-CG", "lg-UG", "lgr-SB", "lif-NP", "liv-RU",
    "lld-IT", "ln-CD", "lo-LA", "lt-LT", "ltg-LV", "lv-LV", "mai-IN", "mdf-RU",
    "mdw-CG", "mhr-RU", "mi-NZ", "mk-MK", "mkw-CG", "ml-IN", "mnc-CN",
    "mni-IN", "mo-MD", "moh-CA", "mos-BF", "mr-IN", "mrj-RU", "ms-MY", "mt-MT",
    "my-MM", "myv-RU", "nds-DE", "ne-NP", "ngz-CG", "nio-RU", "njx-CG",
    "njy-CM", "nl-NL", "nog-RU", "nqo-GN", "nr-ZA", "nso-ZA", "no-NO", "ny-MW",
    "oc-FR", "olo-RU", "om-ET", "or-IN", "pa-IN", "pap-AN", "pjt-AU", "pl-PL",
    "plt-MG", "prs-AF", "ps-AF", "pt-PT", "pui-CO", "puu-GA", "quc-CO",
    "quh-BO", "qul-BO", "qut-GT", "quz-EC", "rm-CH", "ro-RO", "ru-RU",
    "rue-UA", "rw-RW", "sa-IN", "sah-RU", "sat-IN", "sc-IT", "sd-IN", "sdc-IT",
    "sdh-IR", "sdj-CG", "sdn-IT", "se-NO", "seb-YT", "sg-CF", "shs-CA",
    "si-LK", "sid-ET", "sjd-RU", "sje-SE", "sjo-CN", "sk-SK", "sl-SI", "so-SO",
    "sq-AL", "src-IT", "sro-IT", "ss-ZA", "st-ZA", "sv-SE", "sw-KE", "syr-TR",
    "szl-PL", "ta-IN", "te-IN", "tek-CG", "tet-TL", "th-TH", "ti-ET", "tk-TM",
    "tl-PH", "tpi-PG", "tmz-MA", "tn-ZA", "tr-TR", "ts-ZA", "tsa-CG", "tt-RU",
    "ty-PF", "tyx-CG", "udm-RU", "ug-CN", "uk-UA", "ur-PK", "ve-ZA", "vec-IT",
    "vep-RU", "vi-VN", "vif-CG", "vro-EE", "wa-BE", "wo-SN", "xh-ZA", "xku-CG",
    "yi-IL", "yo-NG", "yom-CD", "yrk-RU", "yue-HK", "zu-ZA"
)

langsing = (
    "ar", "bs", "ckb", "cz", "dsb", "dz", "eu", "en", "eo", "fr", "ia", "ie",
    "iu", "jbo", "ks", "la", "mn", "nb", "nn", "pnb", "qtz", "sh", "sma",
    "smj", "smn", "sms", "sr", "tg", "uz", "zh"
)

scripttypes = {
    'west': 1,
    'asian': 2,
    'ctl': 3,
    'rtl': 4,
    'none': ""
}


def zipadd(zipfile, data, fname):
    zinfo = ZipInfo()
    zinfo.filename = fname
    tlocal = time.localtime()
    zinfo.date_time = (
        tlocal[0],
        tlocal[1]+1,
        tlocal[2]+1,
        tlocal[3],
        tlocal[4],
        tlocal[5]
    )
    zinfo.compress_type = ZIP_DEFLATED
    zinfo.external_attr = 0o0664 << 16
    zipfile.writestr(zinfo, data)


def ziphunspell(ozip, hun, name):
    zipadd(ozip, hun.getaff().encode('utf-8'), 'dictionaries/' + name + '.aff')
    zipadd(ozip, hun.getdic().encode('utf-8'), 'dictionaries/' + name + '.dic')


def zipnfcfile(ozip, fin, fout, affix=None):
    dat = ""
    with open(fin) as fd:
        dat += u"\n".join([unicodedata.normalize('NFC', x) for x in fd.readlines()])  # noqa: E501
    if affix is not None:
        with open(affix) as fd:
            dat += u"\n".join([unicodedata.normalize('NFC', x) for x in fd.readlines()])  # noqa: E501
    zipadd(ozip, dat.replace("\uFEFF", ""), fout)


def main():
    parser = ArgumentParser()
    parser.add_argument(
        'langtag',
        help='language tag for this extension'
    )
    parser.add_argument(
        'outfile',
        help='output oxt file'
    )
    parser.add_argument(
        '-w',
        '--word',
        default="",
        help="ASCII punctuation characters that are word forming"
    )
    parser.add_argument(
        '-t',
        '--type',
        default='west',
        help='script type [west, asian, ctl, rtl, none] Use none if libo already knows about the tag.'  # noqa: E501
    )
    parser.add_argument(
        '-f',
        '--font',
        action='append',
        help='Specifies font for semantic font e.g. -f UI_SANS="Times New Roman". May be repeated'  # noqa: E501
    )
    parser.add_argument(
        '-l',
        '--langname',
        help='Language name for UI strings'
    )
    parser.add_argument(
        '-d',
        '--dict',
        help='Wordlist dictionary. For hunspell dictionaries, specify the .aff file. Will try to infer what kind of xml'  # noqa: E501
    )
    parser.add_argument(
        '-a',
        '--affix',
        help='Merge the given affix file data into the generated .aff file'
    )
    parser.add_argument(
        '-v',
        '--version',
        default='0.1',
        help='OXT version number'
    )
    parser.add_argument(
        '--dicttype',
        help='Specifies dictionary type [hunspell, pt, ptall, text]'
    )
    parser.add_argument(
        '--publisher',
        help='Name of publisher'
    )
    parser.add_argument(
        '--puburl',
        default='',
        help='URL of publisher'
    )
    args = parser.parse_args()

    resdir = os.path.join(os.path.dirname(xtmpl.__file__), 'data')
    scripttype = scripttypes.get(args.type.lower(), 1)

    ozip = ZipFile(args.outfile, "w")
    t = xtmpl.Templater()

    fontmap = {}
    if args.font is not None:
        for f in args.font:
            (id, name) = f.split('=')
            fontmap[id] = name
        t.define('fonttypes', " ".join(sorted(fontmap.keys())))
    else:
        t.define('fonttypes', '')

    test = args.langtag + "-"
    for k in langres:
        if k.startswith(test):
            print(f"Can't have unregioned tag {args.langtag}, using {k} instead.")  # noqa: E501
            args.langtag = k
            break

    if args.langname is None:
        args.langname = args.langtag

    def fn_fonts(context, name):
        return fontmap[name]

    t.define('langtag', args.langtag)
    t.define('resdir', resdir)
    t.define('scripttype', str(scripttype))
    t.define('language', args.langname)
    t.define('version', args.version)
    if args.publisher is not None:
        t.define('publisher', args.publisher)
        t.define('puburl', args.puburl)
    else:
        t.define('publisher', '')
    t.addfn(None, 'fonts', fn_fonts)
    t.parse(os.path.join(resdir, 'dictxcu.xml'))
    t.process()
    zipadd(ozip, str(t).encode('utf-8'), 'dictionaries.xcu')

    t.parse(os.path.join(resdir, 'oxtdescription.xml'))
    t.process()
    zipadd(ozip, str(t).encode('utf-8'), 'description.xml')

    license = """LICENSES:
    Spell checker: MIT

    https://opensource.org/licenses/MIT
    """
    zipadd(ozip, license.encode('utf-8'), 'LICENSES-en.txt')

    manifest = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE manifest:manifest PUBLIC "-//OpenOffice.org//DTD Manifest 1.0//EN" "Manifest.dtd">
    <manifest:manifest xmlns:manifest="http://openoffice.org/2001/manifest">
        <manifest:file-entry manifest:media-type="application/vnd.sun.star.configuration-data" manifest:full-path="dictionaries.xcu"/>
    </manifest:manifest>
    """  # noqa: E501
    zipadd(ozip, manifest.encode('utf-8'), 'META-INF/manifest.xml')

    if args.dict:
        if not args.dicttype:
            if args.dict.endswith('.aff'):
                args.dicttype = 'hunspell'
            elif args.dict.endswith('.xml'):
                # should dig into xml, but for now we only know about one type
                args.dicttype = 'pt'
            elif args.dict.endswith('.txt'):
                args.dicttype = 'text'
        if args.dicttype == 'hunspell':
            zipnfcfile(
                ozip,
                args.dict,
                'dictionaries/' + args.langtag + '.aff',
                args.affix
            )
            d = args.dict.replace('.aff', '.dic')
            zipnfcfile(ozip, d, 'dictionaries/' + args.langtag + '.dic', None)
        elif args.dicttype == 'pt' or args.dicttype == 'ptall':
            itemcount = 0
            wordcount = 0
            doc = et.parse(args.dict)
            hun = hs.Hunspell(args.langtag, puncs=args.word)
            for e in doc.findall('//item'):
                itemcount += 1
                if args.dicttype != 'ptall' and e.attrib['spelling'] != 'Correct':  # noqa: E501
                    continue
                hun.addword(str(e.attrib['word']))
                wordcount += 1
            if wordcount * 4 < itemcount:
                # warn if less than 25% of the words are valid
                print(f"Warning: only {wordcount / float(itemcount) * 100:.0f}% of the words marked as correct and entered into the dictionary. Consider using --dicttype ptall")  # noqa: E501
            if args.affix is not None:
                hun.mergeaffix(args.affix)
            ziphunspell(ozip, hun, args.langtag)
        elif args.dicttype == 'text':
            hun = hs.Hunspell(args.langtag, puncs=args.word)
            with codecs.open(args.dict, encoding='utf-8') as infile:
                for line in infile.readlines():
                    hun.addword(line.replace("\uFEFF", "").strip())
            if args.affix is not None:
                hun.mergeaffix(args.affix)
            ziphunspell(ozip, hun, args.langtag)

    ozip.close()


if __name__ == '__main__':
    main()