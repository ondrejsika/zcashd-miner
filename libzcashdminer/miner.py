from __future__ import print_function

import struct
import time


from jsonrpc_requests import Server

from pyzceqsolver.solver import Solver
from utils import hex_to_bin, bin_to_hex, double_sha256_digest, sha256_digest_to_int, pack_varint, replace_output, \
    txs_hashes, get_txs_from_template
from merkletree import MerkleTree


class ZcashdMiner(object):
    def __init__(self, zcashd_url):
        self.solver = Solver()
        self.server = Server(zcashd_url)

    def get_cb_tx(self, template, mining_address=None):
        orig = hex_to_bin(template['coinbasetxn']['data'])
        if not mining_address:
            return orig

        orig_decoded = self.server.decoderawtransaction(template['coinbasetxn']['data'])

        founder_tax_address = orig_decoded['vout'][1]['scriptPubKey']['addresses'][0]
        founder_tax_amount = orig_decoded['vout'][1]['value']
        reward = orig_decoded['vout'][0]['value']

        new_out_tx = hex_to_bin(self.server.createrawtransaction([], {mining_address: reward,
                                                                      founder_tax_address: founder_tax_amount}))
        return replace_output(orig, new_out_tx)

    @staticmethod
    def get_header_from_templete(t, cb_tx, nonce):
        version = t['version']
        previous_block_hash = hex_to_bin(t['previousblockhash'])

        cb_hash = double_sha256_digest(cb_tx)#[::-1]
        # cb_hash = hex_to_bin(t['coinbasetxn']['hash'])[::-1]
        hashes = [cb_hash, ] + txs_hashes(get_txs_from_template(t))
        hash_merkle_root = MerkleTree(hashes).tree_digest()
        time = t['curtime']
        bits = t['bits']

        return ''.join((
            struct.pack("<i", version),
            previous_block_hash[::-1],
            hash_merkle_root,
            '\x00' * 32,
            struct.pack("<I", time),
            hex_to_bin(bits)[::-1],
            nonce,
        ))

    def submit_block(self, template, cb_tx, header_with_solution_bin):
        txs = get_txs_from_template(template)
        block_bin = ''.join((
            header_with_solution_bin,
            pack_varint(len(txs) + 1),
            # hex_to_bin(template['coinbasetxn']['data']),
            cb_tx,
            ''.join(txs),
        ))
        block_hex = bin_to_hex(block_bin)
        result = self.server.submitblock(block_hex)
        return result

    def mine_block(self, mining_address=None):
        template = self.server.getblocktemplate()
        target = long(template['target'], 16)

        nonce_counter = 0
        while True:
            nonce_counter += 1
            nonce_bin = '%32x' % nonce_counter
            cb_tx = self.get_cb_tx(template, mining_address)
            header_bin = self.get_header_from_templete(template, cb_tx, nonce_bin)
            sol_num = self.solver.find_solutions(header_bin)
            for i in range(sol_num):
                solution_bin = self.solver.get_solution(i)
                header_with_solution_bin = header_bin + '\xfd\x40\x05' + solution_bin
                hash_bin = double_sha256_digest(header_with_solution_bin)
                hash_int = sha256_digest_to_int(hash_bin)
                if hash_int < target:
                    self.submit_block(template, cb_tx, header_with_solution_bin)
                    return

    def mine_n_blocks(self, n, mining_address=None):
        for _ in range(n):
            yield self.mine_block(mining_address)
            time.sleep(2)
