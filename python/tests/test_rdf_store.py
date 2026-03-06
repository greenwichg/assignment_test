# -*- coding: utf-8 -*-
import unittest

from rdflib.namespace import RDF

from rdf_store import RDFItemStore, GR
from gilded_rose import Item


class RDFItemStoreTest(unittest.TestCase):

    def setUp(self):
        self.store = RDFItemStore()

    def test_schema_defines_item_types(self):
        types = list(self.store.graph.subjects(RDF.type, GR.ItemType))
        # normal, aged brie, sulfuras, backstage pass, conjured
        self.assertGreaterEqual(len(types), 5)

    def test_item_to_rdf(self):
        item = Item("Aged Brie", 10, 25)
        uri = self.store.item_to_rdf(item, 0)
        self.assertIsNotNone(self.store.graph.value(uri, GR.name))
        self.assertEqual(int(self.store.graph.value(uri, GR.sellIn)), 10)
        self.assertEqual(int(self.store.graph.value(uri, GR.quality)), 25)

    def test_roundtrip(self):
        item = Item("Elixir", 5, 7)
        uri = self.store.item_to_rdf(item, 0)
        self.store.update_quality()
        self.store.rdf_to_item(uri, item)
        self.assertEqual(item.sell_in, 4)
        self.assertEqual(item.quality, 6)

    def test_type_normal(self):
        self.assertEqual(self.store._determine_item_type("Elixir"), GR.NormalItem)

    def test_type_brie(self):
        self.assertEqual(self.store._determine_item_type("Aged Brie"), GR.AgedBrie)

    def test_type_sulfuras(self):
        self.assertEqual(
            self.store._determine_item_type("Sulfuras, Hand of Ragnaros"), GR.Sulfuras
        )

    def test_type_backstage(self):
        self.assertEqual(
            self.store._determine_item_type("Backstage passes to a TAFKAL80ETC concert"),
            GR.BackstagePass,
        )

    def test_type_conjured(self):
        self.assertEqual(
            self.store._determine_item_type("Conjured Mana Cake"), GR.ConjuredItem
        )


if __name__ == "__main__":
    unittest.main()
