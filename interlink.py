from merkle import mtr

class Interlink:
    def __init__(self, blocks=None):
        self.blocks = [] if blocks is None else blocks

    def update(self, block_id, level):
        blocks = self.blocks.copy()
        for i in range(0, level+1):
            if i < len(blocks):
                blocks[i] = block_id
            else:
                blocks.append(block_id)
        return Interlink(blocks=blocks)

    def as_array(self):
        return self.blocks

    def hash(self):
        return mtr(self.as_array())
