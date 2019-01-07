#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from TraceGeneretor import TraceGeneretor
from TrustManager import TrustManager

def main():
	TraceGeneretor.generateCalls()
	TrustManager.computeTrust()

if __name__== "__main__":
  main()