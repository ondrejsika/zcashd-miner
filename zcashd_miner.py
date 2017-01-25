import struct
import time
import argparse

from jsonrpc_requests import Server

from pyzceqsolver.solver import Solver
from utils import hex_to_bin, bin_to_hex, double_sha256_digest, sha256_digest_to_int


parser = argparse.ArgumentParser()
parser.add_argument('zcashd_url', help='Url to Zcashd')
parser.add_argument('block_count', type=int, help='Count of mined blocks')


args = parser.parse_args()


solver = Solver()
server = Server(args.zcashd_url)


def get_block_template():
    return server.getblocktemplate()


def get_header_from_templete(t, nonce):
    version = t['version']
    previous_block_hash = hex_to_bin(t['previousblockhash'])
    hash_merkle_root = hex_to_bin(t['coinbasetxn']['hash'])
    time = t['curtime']
    bits = t['bits']

    return ''.join((
        struct.pack("<i", version),
        previous_block_hash[::-1],
        hash_merkle_root[::-1],
        '\x00' * 32,
        struct.pack("<I", time),
        hex_to_bin(bits)[::-1],
        nonce,
    ))


def submit_block(template, header_with_solution_bin):
    block_bin = ''.join((
        header_with_solution_bin,
        '\x01',
        hex_to_bin(template['coinbasetxn']['data']),
    ))
    block_hex = bin_to_hex(block_bin)
    server.submitblock(block_hex)


def mine(template):
    target = long(template['target'], 16)

    nonce_counter = 0
    while True:
        nonce_counter += 1
        nonce_bin = '%32x' % nonce_counter
        header_bin = get_header_from_templete(template, nonce_bin)
        sol_num = solver.find_solutions(header_bin)
        for i in range(sol_num):
            solution_bin = solver.get_solution(i)
            header_with_solution_bin = header_bin + '\xfd\x40\x05' + solution_bin
            hash_bin = double_sha256_digest(header_with_solution_bin)
            hash_int = sha256_digest_to_int(hash_bin)
            if hash_int < target:
                submit_block(template, header_with_solution_bin)
                return


if __name__ == '__main__':
    for _ in range(args.block_count):
        mine(get_block_template())
        time.sleep(2)
