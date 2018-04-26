#!/bin/bash

OLDDIR=`pwd`
DIR=`dirname "$0"`

cd "$DIR"

if [ -z "`command -v python3`" ]; then
  echo "Error: Unable to run ''python3''. Exiting."
  exit 1
fi

if [ ! -f ./bin/activate ]; then
  echo "####################################"
  echo "Creating Python Virtual Environment."
  echo "####################################"
  python3 -m venv .
fi

if [ "$VIRTUAL_ENV" != "`pwd`" ]; then
  echo "######################################"
  echo "Activating Python Virtual Environment."
  echo "######################################"
  source ./bin/activate
fi

echo "####################################################"
echo "Upgrade pip in the Virtual Environment if necessary."
echo "####################################################"
pip install --upgrade pip

echo "###################################################"
echo "Install required packages into Virtual Environment."
echo "###################################################"
pip install --requirement requirements.txt

echo "######################"
echo "Packaging AllBar.app ."
echo "######################"
./pack.sh

echo "####################################"
echo "Moving AllBar.app to /Applications ."
echo "####################################"
mv ./dist/AllBar.app /Applications/
