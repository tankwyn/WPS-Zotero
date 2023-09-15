#!/usr/bin/env python3

import os
import shutil
import sys
import re
import stat


PKG_PATH = os.path.dirname(os.path.abspath(__file__))
with open(PKG_PATH + os.path.sep + 'js/ver.js') as f:
    VERSION = f.readlines()[0].split('=')[-1].strip()[1:-1]
APPNAME = 'wps-zotero_{}'.format(VERSION)
if os.name == 'posix':
    ADDON_PATH = os.environ['HOME'] + '/.local/share/Kingsoft/wps/jsaddons'
else:
    ADDON_PATH = os.environ['APPDATA'] + '\\kingsoft\\wps\\jsaddons'
XML_PATHS = {
    'jsplugins': ADDON_PATH + os.path.sep + 'jsplugins.xml',
    'publish': ADDON_PATH + os.path.sep + 'publish.xml',
    'authwebsite': ADDON_PATH + os.path.sep + 'authwebsite.xml'
}
PROXY_PATH = ADDON_PATH + os.path.sep + 'proxy.py'

def uninstall():
    def del_rw(action, name, exc):
        os.chmod(name, stat.S_IWRITE)
        os.remove(name)

    if not os.path.isdir(ADDON_PATH):
        return

    for x in os.listdir(ADDON_PATH):
        if os.path.isdir(ADDON_PATH + os.path.sep + x) and 'wps-zotero' in x:
            print('Removing {}'.format(ADDON_PATH + os.path.sep + x))
            shutil.rmtree(ADDON_PATH + os.path.sep + x, onerror=del_rw)

    for fp in XML_PATHS.values():
        if not os.path.isfile(fp):
            continue
        with open(fp) as f:
            xmlStr = f.read()
        records = [(m.start(),m.end()) for m in re.finditer(r'[\ \t]*<.*wps-zotero.*/>\s*', xmlStr)]
        for r in records:
            print('Removing record from {}'.format(fp))
            with open(fp, 'w') as f:
                f.write(xmlStr[:r[0]] + xmlStr[r[1]:])

print('Uninstalling previous installations if there is any ...')
uninstall()
if len(sys.argv) > 1 and sys.argv[1] == '-u':
    sys.exit()

print('Installing')

# Create necessary directory and files
if not os.path.exists(ADDON_PATH):
    os.makedirs(ADDON_PATH, exist_ok=True)
if not os.path.exists(XML_PATHS['jsplugins']):
    with open(XML_PATHS['jsplugins'], 'w') as f:
        f.write('''<jsplugins>
</jsplugins>
''')
if not os.path.exists(XML_PATHS['publish']):
    with open(XML_PATHS['publish'], 'w') as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<jsplugins>
</jsplugins>
''')
if not os.path.exists(XML_PATHS['authwebsite']):
    with open(XML_PATHS['authwebsite'], 'w') as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<websites>
</websites>
''')

# Copy to jsaddons
shutil.copytree(PKG_PATH, ADDON_PATH + os.path.sep + APPNAME)

# Write records to xml files
def register(fp, tagname, record):
    with open(fp) as f:
        content = f.read()
    pos = [m.end() for m in re.finditer(r'<' + tagname + r'>\s*', content)]
    assert(len(pos) > 0)
    i = pos[0]
    with open(fp, 'w') as f:
        f.write(content[:i] + record + os.linesep + content[i:])

rec = '<jsplugin name="wps-zotero" type="wps" url="http://127.0.0.1:3889/" version="{}"/>'.format(VERSION)
register(XML_PATHS['jsplugins'], 'jsplugins', rec)
rec = '<jsplugin url="http://127.0.0.1:3889/" type="wps" enable="enable_dev" install="null" version="{}" name="wps-zotero"/>'.format(VERSION)
register(XML_PATHS['publish'], 'jsplugins', rec)
rec = '<website origin="null" name="wps-zotero" status="enable"/>'
register(XML_PATHS['authwebsite'], 'websites', rec)

print('All done, enjoy!')
print('(run ./install.py -u to uninstall)')
