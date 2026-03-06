# -*- coding: utf-8 -*-

from rdf_store import RDFItemStore


class GildedRose:

    def __init__(self, items):
        self.items = items

    def update_quality(self):
        store = RDFItemStore()

        uris = []
        for idx, item in enumerate(self.items):
            uris.append(store.item_to_rdf(item, idx))

        store.update_quality()

        for uri, item in zip(uris, self.items):
            store.rdf_to_item(uri, item)


class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)
