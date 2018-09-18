from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import math
from tqdm import tqdm
from rx import Observable
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

rpc_connection = AuthServiceProxy("http://%s:%s@%s:%s" %
        (config['daemon']['user'], config['daemon']['password'],
            config['daemon']['host'], config['daemon']['port']))

STARTING_BLOCK = config['fork']['startingblock']

def bits_to_target(bits):
    bitsN = (bits >> 24) & 0xff
    if not (bitsN >= 0x03 and bitsN <= 0x1d):
        raise Exception("First part of bits should be in [0x03, 0x1d]")
    bitsBase = bits & 0xffffff
    if not (bitsBase >= 0x8000 and bitsBase <= 0x7fffff):
        raise Exception("Second part of bits should be in [0x8000, 0x7fffff]")
    return bitsBase << (8 * (bitsN-3))

def level(block_id, target):
    return -int(math.ceil(math.log(float(block_id) / target, 2)))

class Block:
    def __init__(self, header):
        self.id = header['hash']
        self.target = bits_to_target(int(header['bits'], 16))
        self.level = level(int(self.id, 16), self.target)

    def __repr__(self):
        return '<Block%s>' % {'id': self.id, 'target': self.target, 'level': self.level}

class BlockNotFound(Exception):
    pass

def get_block_header(blk):
    BLOCK_NOT_FOUND_ERROR_CODE = -5
    try:
        return rpc_connection.getblockheader(blk)
    except JSONRPCException as err:
        if err.code == BLOCK_NOT_FOUND_ERROR_CODE:
            raise BlockNotFound(blk)
        else:
            raise

def blocks_between(from_block, to_block=None):
    from_block = get_block_header(from_block)
    if to_block is not None:
        to_block = get_block_header(to_block)

    block = from_block
    while block != to_block:
        yield Block(block)
        if 'nextblockhash' not in block:
            break
        block = get_block_header(block['nextblockhash'])

    if to_block is not None:
        yield Block(to_block)


def interlink(best_block):
    interlink = {}
    for blk in tqdm(blocks_between(STARTING_BLOCK, best_block)):
        for i in range(blk.level + 1):
            interlink[i] = blk.id
    return interlink

def get_best_block_hash():
    return rpc_connection.getbestblockhash()

Observable.interval(1000) \
        .map(lambda _: get_best_block_hash()) \
        .distinct_until_changed() \
        .map(interlink) \
        .subscribe(lambda x: print('new interlink', x)) 

while True:
    pass
