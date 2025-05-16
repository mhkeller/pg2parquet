import unittest
import wrappers
import duckdb
import polars as pl
import numpy as np


class TestGeoTypes(unittest.TestCase):
    def setUp(self):
        wrappers.run_sql("""
            CREATE EXTENSION IF NOT EXISTS postgis;
            DROP TABLE IF EXISTS geo_test;
            CREATE TABLE geo_test (
                id SERIAL PRIMARY KEY,
                pt geometry(Point),
                poly geometry(Polygon),
                mpt geometry(MultiPoint),
                mpoly geometry(MultiPolygon),
                ln geometry(LineString),
                mln geometry(MultiLineString)
            );
            INSERT INTO geo_test (pt, poly, mpt, mpoly, ln, mln) VALUES
                (ST_GeomFromText('POINT(1 2)', 4326),
                 ST_GeomFromText('POLYGON((0 0,0 1,1 1,1 0,0 0))', 4326),
                 ST_GeomFromText('MULTIPOINT((1 2),(3 4))', 4326),
                 ST_GeomFromText('MULTIPOLYGON(((0 0,0 1,1 1,1 0,0 0)),((2 2,2 3,3 3,3 2,2 2)))', 4326),
                 ST_GeomFromText('LINESTRING(0 0,1 1,2 2)', 4326),
                 ST_GeomFromText('MULTILINESTRING((0 0,1 1),(2 2,3 3))', 4326)),
                (NULL, NULL, NULL, NULL, NULL, NULL);
        """)

    def test_export_geotypes(self):
        file = wrappers.run_export_table("geo_test", "geo_test", "id")
        # DuckDB can read WKB as BLOB, but not as geometry directly
        duckdb_table = duckdb.read_parquet(file).fetchall()
        self.assertEqual(duckdb_table[0][0], 1)
        self.assertIsInstance(duckdb_table[0][1], bytes)
        self.assertIsInstance(duckdb_table[0][2], bytes)
        self.assertIsInstance(duckdb_table[0][3], bytes)
        self.assertIsInstance(duckdb_table[0][4], bytes)
        self.assertIsInstance(duckdb_table[0][5], bytes)
        self.assertIsInstance(duckdb_table[0][6], bytes)
        self.assertEqual(duckdb_table[1], (2, None, None, None, None, None, None))

        pl_df = pl.read_parquet(file)
        self.assertEqual(pl_df.schema["pt"], pl.Binary)
        self.assertEqual(pl_df.schema["poly"], pl.Binary)
        self.assertEqual(pl_df.schema["mpt"], pl.Binary)
        self.assertEqual(pl_df.schema["mpoly"], pl.Binary)
        self.assertEqual(pl_df.schema["ln"], pl.Binary)
        self.assertEqual(pl_df.schema["mln"], pl.Binary)
        self.assertEqual(pl_df["id"].to_list(), [1, 2])
        self.assertIsInstance(pl_df["pt"][0], bytes)
        self.assertIsInstance(pl_df["poly"][0], bytes)
        self.assertIsInstance(pl_df["mpt"][0], bytes)
        self.assertIsInstance(pl_df["mpoly"][0], bytes)
        self.assertIsInstance(pl_df["ln"][0], bytes)
        self.assertIsInstance(pl_df["mln"][0], bytes)
        self.assertIsNone(pl_df["pt"][1])
        self.assertIsNone(pl_df["poly"][1])
        self.assertIsNone(pl_df["mpt"][1])
        self.assertIsNone(pl_df["mpoly"][1])
        self.assertIsNone(pl_df["ln"][1])
        self.assertIsNone(pl_df["mln"][1])


if __name__ == "__main__":
    unittest.main()
