import argparse
import requests
import concurrent.futures

from time import sleep
from sys import exit
from random import uniform as rand
from datetime import datetime
from rich.progress import track

banner = """

    UPIFINDER
        
        **AUTHOR**: Krisna Pranav
        **Github**: https://github.com/krishpranav
"""
with open("data/general.txt", "r") as suffix_file:
    upi_suffix_dict = suffix_file.read().splitlines() 

with open("data/mobile.txt", "r") as mobile_suffix_file:
    mobile_suffix_dict = mobile_suffix_file.read().splitlines()

with open("data/fastag.txt", "r") as fastag_suffix_file:
    fastag_suffix_dict = fastag_suffix_file.read().splitlines()

with open("data/gpay.txt", "r") as gpay_suffix_file:
    gpay_suffix_dict = gpay_suffix_file.read().splitlines()

def searchvpa(searchtext, vpa_dict, threadcount):
    if(threadcount == 0):
        for suffix in track(vpa_dict, description="querying . . . "):
            try:
                address_discovery(searchtext + '@' + suffix, API_URL)
            except KeyboardInterrupt:
                print('[*] execution interrupted. quitting...')
                exit(0)
    else:
        threadcount = 10 if threadcount > 10 else threadcount
        with concurrent.futures.ThreadPoolExecutor(max_workers=threadcount) as executor:
            try:
                for suffix in vpa_dict:
                    executor.submit(address_discovery, searchtext + '@' + suffix, API_URL)
                    sleep(rand(0.1, 0.2))
            except KeyboardInterrupt:
                executor._threads.clear()
                concurrent.futures.thread._threads_queues.clear()
                print('\n[*] execution interrupted. quitting...')
    print('[i] finished at ' + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    exit(1)

def address_discovery(vpa, api_url):
    
    r = requests.post(api_url, data={'vpa':vpa,'merchant_id':'milaap'}, headers={'Connection':'close'})
    if r.status_code == 200 and r.json()['status'] == 'VALID':
        print('[+] ' + vpa + ' is a valid UPI payment address registered to ' + r.json()['customer_name']) if r.json()['customer_name'] else print('[*] The name associated with the UPI payment address could not be determined')
        
    elif r.status_code == 200 and r.json()['status'] == 'INVALID' and arguments.debug:
        print('[-] query failed for ' + vpa)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='upifinder.py')
    parser.add_argument('-t', '--threads', type=int, default=0, help='number of threads to use for parallel address discovery')
    parser.add_argument('-q', '--quiet', default=False, action='store_true', help='suppress banner')
    parser.add_argument('-d', '--debug', default=False, action='store_true', help='show failed queries')
    
    group_1 = parser.add_mutually_exclusive_group()
    group_1.add_argument('-w', '--wordlist', type=str, nargs='?', help='use wordlist for suffixes')
    group_2 = parser.add_mutually_exclusive_group()
    group_2.add_argument('phone', type=str, nargs='?', help='phone number to query UPI addresses for')
    group_3 = parser.add_mutually_exclusive_group()
    group_3.add_argument('-g', '--gpay', type=str, nargs='?', help='enter gmail address to query Google Pay UPI addresses for')
    group_4 = parser.add_mutually_exclusive_group()
    group_4.add_argument('-v', '--vpa', type=str, nargs='?', help='enter a single VPA to query')
    group_5 = parser.add_mutually_exclusive_group()
    group_5.add_argument('-i', '--identifier', type=str, nargs='?', help='enter an address to query against all providers')
    group_6 = parser.add_mutually_exclusive_group()
    group_6.add_argument('-f', '--fastag', type=str, nargs='?', help='Enter a vehicle number to search for')
    
    arguments = parser.parse_args()
    
    if arguments.quiet is False:
        print(banner)
    
    API_URL = 'https://api.juspay.in/upi/verify-vpa'

    print('[i] starting at ' + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    if arguments.vpa and '@' in arguments.vpa:
        address_discovery(arguments.vpa, API_URL)
    elif arguments.vpa and '@' not in arguments.vpa:
        print('[*] please enter a full, valid UPI address e.g. <identifier>@<provider>')
        exit(0)

    elif arguments.phone:
        searchtext = arguments.phone[2:] if arguments.phone[0:2] == '91' and len(arguments.phone) > 10 else arguments.phone
        if not searchtext.isdigit():
            exit('[*] phone number must be numeric')
        if len(searchtext) != 10:
            print('[*] please enter a valid 10 digit phone number')
            exit(1)
        print('[i] querying {} suffixes for phone number '.format(len(mobile_suffix_dict)) + searchtext)
        searchvpa(searchtext, mobile_suffix_dict, arguments.threads)
    elif arguments.gpay:
        searchtext = arguments.gpay[:-10] if arguments.gpay.endswith('@gmail.com') else arguments.gpay
        print('[i] querying {} suffixes for '.format(len(gpay_suffix_dict)) + searchtext + '@gmail.com')
        searchvpa(searchtext, gpay_suffix_dict, 4) 

    elif arguments.fastag:
        searchtext = 'netc.' + arguments.fastag
        print('[i] querying {} suffixes for vehicle '.format(len(fastag_suffix_dict)) + arguments.fastag)
        searchvpa(searchtext, fastag_suffix_dict, arguments.threads)
    
    elif arguments.identifier:
        searchtext = arguments.identifier if '@' not in arguments.identifier else arguments.identifier.split('@')[0]
        print('[i] querying {} suffixes for identifier '.format(len(upi_suffix_dict)) + searchtext)
        searchvpa(searchtext, upi_suffix_dict, arguments.threads)
    elif arguments.wordlist:
        with open("{}".format(arguments.wordlist), "r") as wordlist_file:
            wordlist = wordlist_file.read().splitlines() 
            print('[i] querying {} addresses from wordlist '.format(len(wordlist)))
            for address in wordlist:
                address_discovery(address, API_URL)
    else:
        print('[*] please enter a valid argument [*]')
        print('[*] usage: upifinder.py -h for help [*]')
        exit(1)
