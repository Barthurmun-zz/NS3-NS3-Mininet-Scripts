#!/bin/bash

echo "Starting 802.11a"
python 80211a.py > wyniki_80211a.txt
echo "Starting 802.11n CA"
python 80211n_CA.py > wyniki_80211n_CA.txt
echo "Starting 802.11n"
python 80211n.py > wyniki_80211n.txt
echo "Starting 802.11ac CA"
python 80211ac_CA.py > wyniki_80211ac_CA.txt
echo "Starting 802.11ac"
python 80211ac.py > wyniki_80211ac.txt

