#!/bin/bash

# Pull the SRC
wget http://pp-sqb.mantma.co.uk/basestation_latest.zip
unzip basestation_latest.zip

# Extract the table we want
sqlite3 -csv -header basestation.sqb "SELECT * FROM aircraft;" > dump.csv

# Do a little cleanup
rm -f basestation*
