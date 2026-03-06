# -*- coding: utf-8 -*-
import os

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, XSD

GR = Namespace("http://example.org/gilded-rose#")


class RDFItemStore:

    def __init__(self):
        self.graph = Graph()
        self.graph.bind("gr", GR)
        schema_path = os.path.join(os.path.dirname(__file__), "schema.ttl")
        self.graph.parse(schema_path, format="turtle")

    def item_to_rdf(self, item, item_id):
        item_uri = URIRef(f"http://example.org/gilded-rose#item_{item_id}")

        self.graph.add((item_uri, RDF.type, GR.Item))
        self.graph.add((item_uri, GR.name, Literal(item.name, datatype=XSD.string)))
        self.graph.add((item_uri, GR.sellIn, Literal(item.sell_in, datatype=XSD.integer)))
        self.graph.add((item_uri, GR.quality, Literal(item.quality, datatype=XSD.integer)))
        self.graph.add((item_uri, GR.itemType, self._determine_item_type(item.name)))

        return item_uri

    def rdf_to_item(self, item_uri, item):
        """Write sellIn/quality back from the graph into the Item object."""
        sell_in = self.graph.value(item_uri, GR.sellIn)
        quality = self.graph.value(item_uri, GR.quality)
        if sell_in is not None:
            item.sell_in = int(sell_in)
        if quality is not None:
            item.quality = int(quality)

    def update_quality(self):
        """Query all items via SPARQL, apply rules, write back."""
        query = """
            SELECT ?item ?type ?sellIn ?quality
            WHERE {
                ?item a gr:Item ;
                      gr:itemType ?type ;
                      gr:sellIn ?sellIn ;
                      gr:quality ?quality .
            }
        """
        rows = list(self.graph.query(query, initNs={"gr": GR}))

        for row in rows:
            sell_in = int(row.sellIn)
            quality = int(row.quality)
            new_sell_in, new_quality = self._apply_rules(row.type, sell_in, quality)

            # swap old triple values for new ones
            self._set_value(row.item, GR.sellIn, sell_in, new_sell_in)
            self._set_value(row.item, GR.quality, quality, new_quality)

    def _apply_rules(self, item_type, sell_in, quality):
        if item_type == GR.Sulfuras:
            return sell_in, quality

        expired = sell_in <= 0
        new_sell_in = sell_in - 1

        if item_type == GR.AgedBrie:
            change = 2 if expired else 1
            return new_sell_in, min(quality + change, 50)

        if item_type == GR.BackstagePass:
            if expired:
                return new_sell_in, 0
            if sell_in <= 5:
                return new_sell_in, min(quality + 3, 50)
            if sell_in <= 10:
                return new_sell_in, min(quality + 2, 50)
            return new_sell_in, min(quality + 1, 50)

        if item_type == GR.ConjuredItem:
            change = 4 if expired else 2
            return new_sell_in, max(quality - change, 0)

        # normal item
        change = 2 if expired else 1
        return new_sell_in, max(quality - change, 0)

    def _set_value(self, subject, predicate, old_val, new_val):
        self.graph.remove((subject, predicate, Literal(old_val, datatype=XSD.integer)))
        self.graph.add((subject, predicate, Literal(new_val, datatype=XSD.integer)))

    def _determine_item_type(self, name):
        if name == "Aged Brie":
            return GR.AgedBrie
        if name == "Sulfuras, Hand of Ragnaros":
            return GR.Sulfuras
        if name.startswith("Backstage passes"):
            return GR.BackstagePass
        if name.startswith("Conjured"):
            return GR.ConjuredItem
        return GR.NormalItem
