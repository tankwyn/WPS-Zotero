#!/bin/bash

# Check if running from current directory
if [ ! -f ./agent.py ]; then
  echo 'Please run this script from where it is located!'
  exit
fi

version=$(cat version.txt)
addon_path=~/.local/share/Kingsoft/wps/jsaddons
jsplugins=${addon_path}/jsplugins.xml
script_path=~/.wps-zotero
app_name="wps-zotero_${version}"

# Check dependencies.
echo 'Checking dependencies'
has_pip3=$(which pip3)
if [ -z "${has_pip3}" ]; then
  echo 'Need python3, pip3 and python package: requests'
  echo 'Please try: sudo apt install python3-pip'
  echo 'Then: pip3 install requests'
  exit
fi
has_requests=$(pip3 show requests)
if [ -z "${has_requests}" ]; then
  echo 'Installing python package: requests.'
  pip3 install requests --break-system-packages
fi

echo 'Checking previous installation'
# Check previous installation
if [ -d ${script_path} ]; then
  if [ -f ${script_path}/wps-zotero-pipe ]; then
    echo 'It appears the addon is still running, please quit WPS, uninstall the previously installed addon and try again.'
    exit
  fi
  echo 'It appears there is a previous installation, please quit WPS, uninstall the previously installed addon and try again.'
  exit
fi
if [ -d ${addon_path}/${app_name} ]; then
  echo 'It appears there is a previous installation, please quit WPS, uninstall the previously installed addon and try again.'
  exit
fi

echo 'Installing'
# Make script path and copy agent.py to it.
mkdir ${script_path}
cp ./agent.py ${script_path}

# Create the addon path if does not exists.
if [ ! -d ${addon_path} ]; then
  mkdir -p ${addon_path}
fi

# Add plugin record to jsplugins.xml
if [ ! -f ${jsplugins} ]; then
  cat << EOF >${jsplugins}
<jsplugins>
  <jsplugin name="wps-zotero" type="wps" url="http://127.0.0.1:3889/" version="${version}"/>
</jsplugins>
EOF
else
  sed -i '/wps-zotero/d' ${jsplugins}
  n0=$(grep -n '<jsplugins>'  ${jsplugins} | cut -d ':' -f 1)
  n1=$(grep -n '</jsplugins>' ${jsplugins} | cut -d ':' -f 1)
  if [ $n0 == $n1 ]; then
    sed -i 's/<jsplugins>/<jsplugins>\n/' ${jsplugins}
  fi
  sed -i "$[n0+1]i\ \ <jsplugin name=\"wps-zotero\" type=\"wps\" url=\"http://127.0.0.1:3889/\" version=\"${version}\"/>" ${jsplugins}
fi

# TODO: add record to publish.xml

# Move 
cp -r . ${addon_path}/${app_name}

echo "Completed, enjoy!"
