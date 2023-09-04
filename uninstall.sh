#!/bin/bash

version=$(cat version.txt)
addon_path=~/.local/share/Kingsoft/wps/jsaddons
jsplugins=${addon_path}/jsplugins.xml
script_path=~/.wps-zotero
app_name="wps-zotero_${version}"

if [ -f ${script_path}/wps-zotero-pipe ]; then
  echo 'It appears the addon is still running, please quit WPS'
  exit
fi

rm -rf ${script_path} 2>/dev/null
rm -rf ${addon_path}/${app_name} 2>/dev/null
if [ -f ${jsplugins} ]; then
  n=$(grep -n "wps-zotero" ${jsplugins} | cut -d ':' -f 1)
  sed -i ${n}d ${jsplugins}
fi

