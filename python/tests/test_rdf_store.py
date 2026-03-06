# -*- coding: utf-8 -*-
import unittest

from rdf_store import RDFItemStore, GR
from gilded_rose import Item


class RDFItemStoreTest(unittest.TestCase):

    def setUp(self):
        self.store = RDFItemStore()

    def test_schema_loaded(self):
        """The schema file should define the ItemType class."""
        from rdflib.namespace import RDF
        types = list(self.store.graph.subjects(RDF.type, GR.ItemType))
        self.assertGreaterEqual(len(types), 5)

    def test_item_to_rdf_creates_triples(self):
        item = Item("Aged Brie", 10, 25)
        uri = self.store.item_to_rdf(item, 0)
        self.assertIsNotNone(self.store.graph.value(uri, GR.name))
        self.assertEqual(int(self.store.graph.value(uri, GR.sellIn)), 10)
        self.assertEqual(int(self.store.graph.value(uri, GR.quality)), 25)

    def test_rdf_to_item_syncs_values(self):
        item = Item("Elixir", 5, 7)
        uri = self.store.item_to_rdf(item, 0)
        self.store.update_quality()
        self.store.rdf_to_item(uri, item)
        self.assertEqual(item.sell_in, 4)
        self.assertEqual(item.quality, 6)

    def test_determine_item_type_normal(self):
        self.assertEqual(self.store._determine_item_type("Elixir"), GR.NormalItem)

    def test_determine_item_type_aged_brie(self):
        self.assertEqual(self.store._determine_item_type("Aged Brie"), GR.AgedBrie)

    def test_determine_item_type_sulfuras(self):
        self.assertEqual(
            self.store._determine_item_type("Sulfuras, Hand of Ragnaros"),
            GR.Sulfuras,
        )

    def test_determine_item_type_backstage(self):
        self.assertEqual(
            self.store._determine_item_type("Backstage passes to a TAFKAL80ETC concert"),
            GR.BackstagePass,
        )

    def test_determine_item_type_conjured(self):
        self.assertEqual(
            self.store._determine_item_type("Conjured Mana Cake"),
            GR.ConjuredItem,
        )

    def test_serialize_returns_turtle(self):
        item = Item("foo", 1, 1)
        self.store.item_to_rdf(item, 0)
        output = self.store.serialize()
        self.assertIn("gr:name", output)


if __name__ == "__main__":
    unittest.main()
