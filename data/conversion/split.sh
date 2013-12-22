#!/bin/bash

cat NATFIX.txt | grep ARPT > ARPT.txt
cat NATFIX.txt | grep GPS-WP > GPS-WP.txt
cat NATFIX.txt | grep MIL-REP > MIL-REP.txt
cat NATFIX.txt | grep MIL-WAY > MIL-WAY.txt
cat NATFIX.txt | grep NRS-WAY > NRS-WAY.txt
cat NATFIX.txt | grep RADAR > RADAR.txt
cat NATFIX.txt | grep REP-PT > REP-PT.txt
cat NATFIX.txt | grep RNAV-WP > RNAV-WP.txt
cat NATFIX.txt | grep WAYPOIN > WAYPOIN.txt