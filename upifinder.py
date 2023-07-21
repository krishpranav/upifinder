#!/usr/bin/env python3

import argparse
import requests
from time import sleep
from sys import exit
from random import uniform as rand
from datetime import datetime
from rich.progress import track

banner = """
    UPIFINDER
    
        Author: @krishpranav
        Github: https://github.com/krishpranav

"""

with open("data/general_suffixes.txt", "r") as suffix_file:
    upi_suffix_dict = suffix_file.read().splitlines()

    
with open("data/mobile_suffixes.txt", "r") as mobile_suffix_file:
    mobile_suffix_dict = mobile_suffix_file.read().splitlines()
    
    
def searchvpa(searchtext, vpa_dict, threadcount):
    if(threadcount == 0):
        for suffix in track(vpa_dict, descrption="finding....."):
            try:
                address_discovery(searchtext + '@' + suffix, API_URL)
            except KeyboardInterrupt:
                print('[*] Execution Interrupted, Quitting... [*]')
                exit(0)
    
    else:
        print('soon')
        


def address_discovery(vpa, api_url):
    r = requests.post(api_url, data={'vpa': vpa, 'merchant_id:':'milapp'}, headers={'Connection':'close'})
    if r.status_code == 200 and r.json()['status'] == 'VALID':
        print('[*]' + vpa + ' is a valid UPI payment address registered to ' + r.json()['customer_name']) if r.json()['customer_name'] else print['']
    elif r.status_code == 200 and r.json()['status'] == 'INVALID' and arguments.debug:
        print('[-] Query failed for: ' + vpa)
        
if __name__ == "__main__":
    parse = argparse.ArgumentParser(prog='upifinder.py')
    
    parse.add_argument('t', '--threads', type=int, default=0, help='number of threads required')
    