# -*- coding: utf-8 -*-
"""
RDF Store for Gilded Rose inventory management.

This module converts Items to/from RDF representation and performs
quality updates using RDF/SPARQL operations.
"""

import os

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, XSD

GR = Namespace("http://example.org/gilded-rose#")


class RDFItemStore:
    """Manages items as RDF triples and provides methods for quality updates."""

    def __init__(self):
        self.graph = Graph()
        self.graph.bind("gr", GR)
        self._load_schema()

    def _load_schema(self):
        schema_path = os.path.join(os.path.dirname(__file__), "schema.ttl")
        self.graph.parse(schema_path, format="turtle")

    def item_to_rdf(self, item, item_id: int) -> URIRef:
        """Convert an Item object to RDF triples and add to the graph."""
        item_uri = URIRef(f"http://example.org/gilded-rose#item_{item_id}")

        self.graph.add((item_uri, RDF.type, GR.Item))
        self.graph.add((item_uri, GR.name, Literal(item.name, datatype=XSD.string)))
        self.graph.add((item_uri, GR.sellIn, Literal(item.sell_in, datatype=XSD.integer)))
        self.graph.add((item_uri, GR.quality, Literal(item.quality, datatype=XSD.integer)))
        self.graph.add((item_uri, GR.itemType, self._determine_item_type(item.name)))

        return item_uri

    def rdf_to_item(self, item_uri: URIRef, item):
        """Sync RDF data back to the Item object."""
        sell_in = self.graph.value(item_uri, GR.sellIn)
        quality = self.graph.value(item_uri, GR.quality)

        if sell_in is not None:
            item.sell_in = int(sell_in)
        if quality is not None:
            item.quality = int(quality)

    def update_quality(self):
        """
        Apply the Gilded Rose business rules to every item in the graph.

        Uses SPARQL to query items by type, then applies the appropriate
        quality/sellIn adjustments in Python and writes them back.
        """
        items_query = """
            SELECT ?item ?type ?sellIn ?quality
            WHERE {
                ?item a gr:Item ;
                      gr:itemType ?type ;
                      gr:sellIn ?sellIn ;
                      gr:quality ?quality .
            }
        """
        results = list(self.graph.query(items_query, initNs={"gr": GR}))

        for row in results:
            item_uri = row.item
            item_type = row.type
            sell_in = int(row.sellIn)
            quality = int(row.quality)

            new_sell_in, new_quality = self._apply_rules(item_type, sell_in, quality)

            self._update_triple(item_uri, GR.sellIn, sell_in, new_sell_in)
            self._update_triple(item_uri, GR.quality, quality, new_quality)

    def _apply_rules(self, item_type, sell_in, quality):
        """Return (new_sell_in, new_quality) after applying the business rules."""
        if item_type == GR.Sulfuras:
            return sell_in, quality

        new_sell_in = sell_in - 1
        expired = sell_in <= 0

        if item_type == GR.AgedBrie:
            delta = 2 if expired else 1
            new_quality = min(quality + delta, 50)

        elif item_type == GR.BackstagePass:
            if expired:
                new_quality = 0
            elif sell_in <= 5:
                new_quality = min(quality + 3, 50)
            elif sell_in <= 10:
                new_quality = min(quality + 2, 50)
            else:
                new_quality = min(quality + 1, 50)

        elif item_type == GR.ConjuredItem:
            delta = 4 if expired else 2
            new_quality = max(quality - delta, 0)

        else:
            delta = 2 if expired else 1
            new_quality = max(quality - delta, 0)

        return new_sell_in, new_quality

    def _update_triple(self, subject, predicate, old_val, new_val):
        """Replace a single integer-valued triple."""
        self.graph.remove((subject, predicate, Literal(old_val, datatype=XSD.integer)))
        self.graph.add((subject, predicate, Literal(new_val, datatype=XSD.integer)))

    def _determine_item_type(self, name: str) -> URIRef:
        """Map an item name to its RDF item-type URI."""
        if name == "Aged Brie":
            return GR.AgedBrie
        if name == "Sulfuras, Hand of Ragnaros":
            return GR.Sulfuras
        if name.startswith("Backstage passes"):
            return GR.BackstagePass
        if name.startswith("Conjured"):
            return GR.ConjuredItem
        return GR.NormalItem

    def serialize(self, fmt="turtle"):
        """Return the current graph serialized in the given format."""
        return self.graph.serialize(format=fmt)
