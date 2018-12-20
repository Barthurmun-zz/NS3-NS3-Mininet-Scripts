#!/bin/bash
#Author: Jakub Bryl


echo "Starting 802.11a"
python 80211a.py > wyniki_80211a.txt

echo "Starting 802.11a_2sta"
python 80211a_2sta.py > wyniki_80211a_2sta.txt

echo "Starting 802.11a_5sta"
python 80211a_5sta.py > wyniki_80211a_5sta.txt

echo "Starting 802.11n"
python 80211n.py > wyniki_80211n.txt

echo "Starting 802.11n_2sta"
python 80211n_2sta.py > wyniki_80211n_2sta.txt

echo "Starting 802.11n_5sta"
python 80211n_5sta.py > wyniki_80211n_5sta.txt

echo "Starting 802.11ac"
python 80211ac.py > wyniki_80211ac.txt

echo "Starting 802.11ac_2sta"
python 80211ac_2sta.py > wyniki_80211ac_2sta.txt

echo "Starting 802.11ac_5sta"
python 80211ac_5sta.py > wyniki_80211ac_5sta.txt

echo "Starting 802.11n_CA"
python 80211n_CA.py > wyniki_80211n_CA.txt

echo "Starting 802.11n_CA_2sta"
python 80211n_CA_2sta.py > wyniki_80211n_CA_2sta.txt

echo "Starting 802.11n_CA_5sta"
python 80211n_CA_5sta.py > wyniki_80211n_CA_5sta.txt

echo "Starting 802.11ac_CA"
python 80211ac_CA.py > wyniki_80211ac_CA.txt

echo "Starting 802.11ac_CA_2sta"
python 80211ac_CA_2sta.py > wyniki_80211ac_CA_2sta.txt

echo "Starting 802.11ac_CA_5sta"
python 80211ac_CA_5sta.py > wyniki_80211ac_CA_5sta.txt
