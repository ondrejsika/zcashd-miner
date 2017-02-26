from __future__ import print_function

import argparse

from libzcashdminer import ZcashdMiner


parser = argparse.ArgumentParser()
parser.add_argument('zcashd_url', help='Url to Zcashd')
parser.add_argument('block_count', type=int, help='Count of mined blocks')
parser.add_argument('-a', '--address', default=None, help='Mining address')

args = parser.parse_args()

miner = ZcashdMiner(args.zcashd_url)
for result in miner.mine_n_blocks(args.block_count, args.address):
    if not result:
        print('OK')
    else:
        print('ERR %s' % result)
