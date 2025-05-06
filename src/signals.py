#!/usr/bin/env python
from signal import signal, SIGINT
from sys import exit

def sigint(sig, frame):
    print(end='\r')
    exit()

signal(SIGINT, sigint)
