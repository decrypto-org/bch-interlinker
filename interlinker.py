from collections import deque
from os import path
from time import sleep
import configparser
import logging
import math
import shelve

from bitcoin.core import CMutableTxOut, CScript, CMutableTransaction, OP_RETURN
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from xdg.BaseDirectory import save_cache_path, save_config_path

from interlink import Interlink

VELVET_FORK_GENESIS = '00000000000001934669a81ecfaa64735597751ac5ca78c4d8f345f11c2237cf'
MAX_TARGET = 0xffff0000000000000000000000000000000000000000000000000000

def level(block_id, target=None):
    target = MAX_TARGET if target is None else target
    if isinstance(block_id, str):
        block_id = int(block_id, 16)
    return -int(math.ceil(math.log(float(block_id) / target, 2)))

def prev(block_id):
    return rpc.getblockheader(block_id)['previousblockhash']

def genesis_interlink():
    return Interlink(genesis=VELVET_FORK_GENESIS).update(VELVET_FORK_GENESIS,
            level(VELVET_FORK_GENESIS))

def interlink(tip_id, store=None):
    store = {} if store is None else store
    intermediate_block_ids = deque()
    intermediate_id = tip_id
    if VELVET_FORK_GENESIS not in store:
        store[VELVET_FORK_GENESIS] = genesis_interlink()
    while intermediate_id not in store:
        intermediate_block_ids.appendleft(intermediate_id)
        intermediate_id = prev(intermediate_id)

    intermediate_interlink = store[intermediate_id]
    for block_id in intermediate_block_ids:
        intermediate_interlink = store[block_id] = \
                intermediate_interlink.update(block_id, level(block_id))
    return intermediate_interlink

def create_raw_velvet_tx(payload_buf):
    VELVET_FORK_MARKER = b'interlink'
    digest_outs = [CMutableTxOut(0, CScript([OP_RETURN, VELVET_FORK_MARKER, payload_buf]))]
    tx = CMutableTransaction([], digest_outs)
    return tx.serialize().hex()

def send_velvet_tx(payload_buf):
    change_address = rpc.getaccountaddress("")
    funded_raw_tx = rpc.fundrawtransaction(create_raw_velvet_tx(payload_buf),
            {'changeAddress': change_address})['hex']
    signed_funded_raw_tx = rpc.signrawtransaction(funded_raw_tx)['hex']
    return rpc.sendrawtransaction(signed_funded_raw_tx)

def main():
    global rpc
    APP_NAME = 'bch-interlinker'
    NEW_TIP_CHECK_INTERVAL_SECONDS = 5

    config_path = save_config_path(APP_NAME)
    cache_path = save_cache_path(APP_NAME)
    db_path = path.join(cache_path, 'db')
    config_file_path = path.join(config_path, 'config.ini')

    config = configparser.ConfigParser()
    config.read(config_file_path)

    rpc = AuthServiceProxy("http://%s:%s@%s:%s" %
            (config['daemon']['user'], config['daemon']['password'],
                config['daemon']['host'], config['daemon']['port']))

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%y %H:%M:%S %Z')
    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.DEBUG)

    tip_id = ''
    while True:
        possibly_new_tip_id = rpc.getbestblockhash()
        if possibly_new_tip_id == tip_id:
            sleep(NEW_TIP_CHECK_INTERVAL_SECONDS)
            continue
        tip_id = possibly_new_tip_id
        logger.info('new block "%s"', tip_id)
        with shelve.open(db_path) as db:
            new_interlink = interlink(tip_id, db)
        logger.debug('new interlink "%s"', new_interlink.as_array())
        logger.info('mtr hash "%s"', new_interlink.hash().hex())
        logger.info('velvet tx "%s"', send_velvet_tx(new_interlink.hash()))

if __name__ == '__main__':
    main()
