# -*- coding: utf-8 -*-

from rdf_store import RDFItemStore


class GildedRose:
    """Gilded Rose inventory system backed by an RDF store."""

    def __init__(self, items):
        self.items = items

    def update_quality(self):
        """Load items into an RDF graph, apply business rules, sync back."""
        store = RDFItemStore()

        # convert every Item into RDF triples
        uris = []
        for idx, item in enumerate(self.items):
            uri = store.item_to_rdf(item, idx)
            uris.append(uri)

        # run the quality-update logic on the RDF graph
        store.update_quality()

        # write updated values back to the original Item objects
        for uri, item in zip(uris, self.items):
            store.rdf_to_item(uri, item)


class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)
