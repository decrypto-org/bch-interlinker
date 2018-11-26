import configparser
import logging
import math
from collections import deque
import shelve

from bitcoin.core import CMutableTxOut, CScript, CMutableTransaction, OP_RETURN
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from tqdm import tqdm

from interlink import Interlink

config = configparser.ConfigParser()
config.read('config.ini')

rpc = AuthServiceProxy("http://%s:%s@%s:%s" %
        (config['daemon']['user'], config['daemon']['password'],
            config['daemon']['host'], config['daemon']['port']))

VELVET_FORK_GENESIS = config['fork']['startingblock']
MAX_TARGET = int(config['nipopows']['maxtarget'], 16)

def level(block_id, target=MAX_TARGET):
    if isinstance(block_id, str):
        block_id = int(block_id, 16)
    return -int(math.ceil(math.log(float(block_id) / target, 2)))

def prev(block_id):
    return rpc.getblockheader(block_id)['previousblockhash']

def interlink(tip_id, interlink_store=None):
    interlink_store = {} if interlink_store is None else interlink_store
    intermediate_block_ids = deque()
    intermediate_id = tip_id
    while intermediate_id not in interlink_store:
        if intermediate_id == VELVET_FORK_GENESIS:
            interlink_store[intermediate_id] = Interlink().update(intermediate_id, level(intermediate_id))
            break
        intermediate_block_ids.appendleft(intermediate_id)
        intermediate_id = prev(intermediate_id)

    intermediate_interlink = interlink_store[intermediate_id]
    for block_id in intermediate_block_ids:
        intermediate_interlink = intermediate_interlink.update(block_id, level(block_id))
    interlink_store[tip_id] = intermediate_interlink
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

if __name__ == '__main__':
    from time import sleep
    from os import path
    from xdg.BaseDirectory import save_cache_path

    APP_NAME = 'bch-interlinker'
    NEW_TIP_CHECK_INTERVAL_SECONDS = 5

    cache_path = save_cache_path(APP_NAME)
    db_path = path.join(cache_path, 'db')

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p %Z')
    logger = logging.getLogger('interlinker')
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
