# -*- coding: utf-8 -*-
import unittest

from gilded_rose import Item, GildedRose


class GildedRoseTest(unittest.TestCase):
    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------
    def _update(self, name, sell_in, quality):
        item = Item(name, sell_in, quality)
        GildedRose([item]).update_quality()
        return item

    # ------------------------------------------------------------------
    # Normal items
    # ------------------------------------------------------------------
    def test_normal_item_decreases_quality(self):
        item = self._update("Elixir", 10, 20)
        self.assertEqual(item.sell_in, 9)
        self.assertEqual(item.quality, 19)

    def test_normal_item_degrades_twice_after_sell_date(self):
        item = self._update("Elixir", 0, 10)
        self.assertEqual(item.quality, 8)

    def test_quality_never_negative(self):
        item = self._update("Elixir", 5, 0)
        self.assertEqual(item.quality, 0)

    def test_quality_never_negative_past_sell_date(self):
        item = self._update("Elixir", -1, 1)
        self.assertEqual(item.quality, 0)

    # ------------------------------------------------------------------
    # Aged Brie
    # ------------------------------------------------------------------
    def test_aged_brie_increases_quality(self):
        item = self._update("Aged Brie", 5, 10)
        self.assertEqual(item.quality, 11)

    def test_aged_brie_increases_twice_after_sell_date(self):
        item = self._update("Aged Brie", 0, 10)
        self.assertEqual(item.quality, 12)

    def test_aged_brie_quality_caps_at_50(self):
        item = self._update("Aged Brie", 5, 50)
        self.assertEqual(item.quality, 50)

    # ------------------------------------------------------------------
    # Sulfuras
    # ------------------------------------------------------------------
    def test_sulfuras_never_changes(self):
        item = self._update("Sulfuras, Hand of Ragnaros", 0, 80)
        self.assertEqual(item.sell_in, 0)
        self.assertEqual(item.quality, 80)

    def test_sulfuras_negative_sell_in_stays(self):
        item = self._update("Sulfuras, Hand of Ragnaros", -1, 80)
        self.assertEqual(item.sell_in, -1)
        self.assertEqual(item.quality, 80)

    # ------------------------------------------------------------------
    # Backstage passes
    # ------------------------------------------------------------------
    def test_backstage_increases_by_1_when_more_than_10_days(self):
        item = self._update("Backstage passes to a TAFKAL80ETC concert", 15, 20)
        self.assertEqual(item.quality, 21)

    def test_backstage_increases_by_2_when_10_days_or_less(self):
        item = self._update("Backstage passes to a TAFKAL80ETC concert", 10, 20)
        self.assertEqual(item.quality, 22)

    def test_backstage_increases_by_3_when_5_days_or_less(self):
        item = self._update("Backstage passes to a TAFKAL80ETC concert", 5, 20)
        self.assertEqual(item.quality, 23)

    def test_backstage_drops_to_zero_after_concert(self):
        item = self._update("Backstage passes to a TAFKAL80ETC concert", 0, 50)
        self.assertEqual(item.quality, 0)

    def test_backstage_quality_caps_at_50(self):
        item = self._update("Backstage passes to a TAFKAL80ETC concert", 5, 49)
        self.assertEqual(item.quality, 50)

    # ------------------------------------------------------------------
    # Conjured items
    # ------------------------------------------------------------------
    def test_conjured_degrades_twice_as_fast(self):
        item = self._update("Conjured Mana Cake", 3, 6)
        self.assertEqual(item.sell_in, 2)
        self.assertEqual(item.quality, 4)

    def test_conjured_degrades_four_times_after_sell_date(self):
        item = self._update("Conjured Mana Cake", 0, 10)
        self.assertEqual(item.quality, 6)

    def test_conjured_quality_never_negative(self):
        item = self._update("Conjured Mana Cake", 0, 1)
        self.assertEqual(item.quality, 0)

    # ------------------------------------------------------------------
    # RDF integration
    # ------------------------------------------------------------------
    def test_multiple_items_update_correctly(self):
        items = [
            Item("+5 Dexterity Vest", 10, 20),
            Item("Aged Brie", 2, 0),
            Item("Sulfuras, Hand of Ragnaros", 0, 80),
            Item("Conjured Mana Cake", 3, 6),
        ]
        GildedRose(items).update_quality()

        self.assertEqual(items[0].quality, 19)
        self.assertEqual(items[1].quality, 1)
        self.assertEqual(items[2].quality, 80)
        self.assertEqual(items[3].quality, 4)

    def test_item_name_does_not_change(self):
        item = self._update("foo", 0, 0)
        self.assertEqual(item.name, "foo")


if __name__ == "__main__":
    unittest.main()
