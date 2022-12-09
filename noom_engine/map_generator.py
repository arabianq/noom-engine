DEFAULT_MAP = [
    "WWWWWWWWWWWWWW",
    "W............W",
    "W............W",
    "W............W",
    "W............W",
    "W............W",
    "W............W",
    "W............W",
    "W............W",
    "W............W",
    "WWWWWWWWWWWWWW"
]


class Map:
    def __init__(self, tile_size, text_map=None):

        if text_map is None:
            self.TEXT_MAP = DEFAULT_MAP
        else:
            self.TEXT_MAP = text_map

        self.TILE_SIZE = tile_size

    def create_map(self) -> set:
        map_ = set()
        for i, row in enumerate(self.TEXT_MAP):
            for j, char in enumerate(row):
                if char == "W":
                    map_.add((j * self.TILE_SIZE, i * self.TILE_SIZE))
        return map_
