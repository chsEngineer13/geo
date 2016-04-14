#!/bin/bash

set -e

confirm_continue(){
  while true; do
    read -p "=> Are you sure you want to continue? " yn
    case $yn in
      [Yy]* ) break;;
      [Nn]* ) echo "    Aborted script.";exit;;
      * ) echo "    Please answer yes or no.";;
    esac
  done
}

maploom_dev()
{
  echo "  This script will modify the vm to point to your local MapLoom repo"
  echo "  Make sure the /Maploom folder is sym-linked to the MapLoom folder on the host machine"
  echo "  The /Maploom folder should be a git repository clone that has been built using grunt."

  confirm_continue

  [ ! -d /MapLoom ] && echo 'Directory /Maploom not found. have you linked it to Maploom repo on host?'
  [ ! -f /MapLoom/build/maploom.html ] && echo '/MapLoom/build/maploom.html not found. have you built maploom? e.g. \"grunt watch\" '

  rm -rf /vagrant/.venv/lib/python2.7/site-packages/maploom/static/maploom/*
  ln -s /MapLoom/build/* /vagrant/.venv/lib/python2.7/site-packages/maploom/static/maploom/
  rm /vagrant/.venv/lib/python2.7/site-packages/maploom/templates/maps/maploom.html
  ln -s /MapLoom/build/maploom.html /vagrant/.venv/lib/python2.7/site-packages/maploom/templates/maps/maploom.html
}

maploom_dev
