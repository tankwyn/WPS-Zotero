#!/bin/bash

version=$(cat version.txt)
app_name="wps-zotero_${version}"

mkdir build/${app_name}
cp -r agent.py images index.html install.sh uninstall.sh js main.js ribbon.xml version.txt build/${app_name}
cd build
tar zcf ${app_name}.tar.gz ${app_name}
rm -r ${app_name}
