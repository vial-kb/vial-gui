# SPDX-License-Identifier: GPL-2.0-or-later

# Based on https://github.com/ijprest/kle-serial
# & see https://github.com/ijprest/kle-serial/pull/1
import json
from copy import copy


class KeyDefaults:

    def __init__(self):
        self.textColor = "#000000"
        self.textSize = 3


class Key:

    def __init__(self):
        self.color = "#cccccc"
        self.labels = []
        self.textColor = [None] * 12
        self.textSize = []
        self.default = KeyDefaults()
        self.x = 0
        self.y = 0
        self.width = 1
        self.height = 1
        self.x2 = 0
        self.y2 = 0
        self.width2 = 1
        self.height2 = 1
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_angle = 0
        self.decal = False
        self.ghost = False
        self.stepped = False
        self.nub = False
        self.profile = ""
        self.sm = ""
        self.sb = ""
        self.st = ""


class KeyboardMetadata:

    def __init__(self):
        self.author = ""
        self.backcolor = "#eeeeee"
        self.background = None
        self.name = ""
        self.notes = ""
        self.radii = ""
        self.switchBrand = ""
        self.switchMount = ""
        self.switchType = ""


class Keyboard:

    def __init__(self):
        self.meta = KeyboardMetadata()
        self.keys = []


class Cluster:

    def __init__(self):
        self.x = self.y = 0


class Serial:

    labelMap = [
        # 0  1  2  3  4  5  6  7  8  9 10 11   # align flags
        [ 0, 6, 2, 8, 9,11, 3, 5, 1, 4, 7,10], # 0 = no centering
        [ 1, 7,-1,-1, 9,11, 4,-1,-1,-1,-1,10], # 1 = center x
        [ 3,-1, 5,-1, 9,11,-1,-1, 4,-1,-1,10], # 2 = center y
        [ 4,-1,-1,-1, 9,11,-1,-1,-1,-1,-1,10], # 3 = center x & y
        [ 0, 6, 2, 8,10,-1, 3, 5, 1, 4, 7,-1], # 4 = center front (default)
        [ 1, 7,-1,-1,10,-1, 4,-1,-1,-1,-1,-1], # 5 = center front & x
        [ 3,-1, 5,-1,10,-1,-1,-1, 4,-1,-1,-1], # 6 = center front & y
        [ 4,-1,-1,-1,10,-1,-1,-1,-1,-1,-1,-1], # 7 = center front & x & y
    ]

    def reorderLabelsIn(self, labels, align):
        ret = [None] * 12
        for i in range(len(labels)):
            if labels[i]:
                ret[self.labelMap[align][i]] = labels[i]
        return ret

    def deserializeError(self, msg, data):
        raise RuntimeError("Error: {} {}".format(msg, data))
    
    def deserialize(self, rows):
        current = Key()
        cluster = Cluster()
        kbd = Keyboard()
        align = 4
        item = None

        for r in range(len(rows)):
            if isinstance(rows[r], list):
                for k in range(len(rows[r])):
                    item = rows[r][k]
                    if isinstance(item, str):
                        newKey = copy(current)

                        # Calculate some generated values
                        newKey.width2 = current.width if newKey.width2 == 0 else current.width2
                        newKey.height2 = current.height if newKey.height2 == 0 else current.height2
                        newKey.labels = self.reorderLabelsIn(item.split("\n"), align)
                        newKey.textSize = self.reorderLabelsIn(newKey.textSize, align)

                        # Clean up the data
                        for i in range(12):
                            if newKey.labels[i] is None:
                                newKey.textSize[i] = newKey.textColor[i] = None
                            if newKey.textSize[i] == newKey.default.textSize:
                                newKey.textSize[i] = None
                            if newKey.textColor[i] == newKey.default.textColor:
                                newKey.textColor[i] = None
                        
                        # Add the key!
                        kbd.keys.append(newKey)

                        # Set up for the next key
                        current.x += current.width
                        current.width = current.height = 1
                        current.x2 = current.y2 = current.width2 = current.height2 = 0
                        current.nub = current.stepped = current.decal = False
                    else:
                        if k != 0 and ("r" in item or "rx" in item or "ry" in item):
                            self.deserializeError("rotation can only be specified on the first key in a row", item)
                        if "r" in item:
                            current.rotation_angle = item["r"]
                        if "rx" in item:
                            current.rotation_x = cluster.x = item["rx"]
                            current.x = cluster.x
                            current.y = cluster.y
                        if "ry" in item:
                            current.rotation_y = cluster.y = item["ry"]
                            current.x = cluster.x
                            current.y = cluster.y
                        if "a" in item:
                            align = item["a"]
                        if "f" in item:
                            current.default.textSize = item["f"]
                            current.textSize = []
                        if "f2" in item:
                            for i in range(1, 12):
                                current.textSize[i] = item["f2"]
                        if "fa" in item:
                            current.textSize = item["fa"]
                        if "p" in item:
                            current.profile = item["p"]
                        if "c" in item:
                            current.color = item["c"]
                        if "t" in item:
                            split = item["t"].split("\n")
                            if split[0] != "":
                                current.default.textColor = split[0]
                            current.textColor = self.reorderLabelsIn(split, align)
                        if "x" in item:
                            current.x += item["x"]
                        if "y" in item:
                            current.y += item["y"]
                        if "w" in item:
                            current.width = current.width2 = item["w"]
                        if "h" in item:
                            current.height = current.height2 = item["h"]
                        if "x2" in item:
                            current.x2 = item["x2"]
                        if "y2" in item:
                            current.y2 = item["y2"]
                        if "w2" in item:
                            current.width2 = item["w2"]
                        if "h2" in item:
                            current.height2 = item["h2"]
                        if "n" in item:
                            current.nub = item["n"]
                        if "l" in item:
                            current.stepped = item["l"]
                        if "d" in item:
                            current.decal = item["d"]
                        if "g" in item and item["g"]:
                            current.ghost = item.g
                        if "sm" in item:
                            current.sm = item["sm"]
                        if "sb" in item:
                            current.sb = item["sb"]
                        if "st" in item:
                            current.st = item["st"]

                # End of the row
                current.y += 1
                current.x = current.rotation_x
            elif isinstance(item, dict):
                if r != 0:
                    self.deserializeError("keyboard metadata must the be first element", rows[r])
                # TODO: parse prop
            else:
                pass
                # self.deserializeError("unexpected", rows[r])
                # TODO: first item could be {"name": "something"} - should handle it
        return kbd


# TODO: add tests
