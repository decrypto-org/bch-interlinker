from merkle import mtr

class Interlink:
    def __init__(self):
        self.levels = {}

    def update(self, block_id, level):
        deprecated_levels = [existing_level for existing_level in
                sorted(self.levels.keys()) if existing_level <= level]
        for deprecated_level in deprecated_levels:
            del self.levels[deprecated_level]
        self.levels[level] = block_id

    def __getitem__(self, req_level):
        for level in sorted(self.levels.keys()):
            if req_level <= level:
                return self.levels[level]

    def as_array(self):
        array = []
        prev_lvl = -1
        for lvl in sorted(self.levels.keys()):
            array += [self.levels[lvl]] * (lvl - prev_lvl)
            prev_lvl = lvl
        return array

    def hash(self):
        return mtr(self.as_array())
