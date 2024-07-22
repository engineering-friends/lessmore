import asyncio
import os

from itertools import groupby

from learn_language_magic.ask import ask
from learn_language_magic.deps import Deps
from learn_language_magic.notion_rate_limited_client import NotionRateLimitedClient
from learn_language_magic.update_words.flatten_word_collection import flatten_word_collection
from learn_language_magic.update_words.upsert_anki_deck import upsert_anki_deck
from learn_language_magic.update_words.word import Word
from learn_language_magic.update_words.word_collection import word_collection
from lessmore.utils.asynchronous.async_cached_property import prefetch_all_cached_properties
from lessmore.utils.functional.skip_duplicates import skip_duplicates
from loguru import logger
from more_itertools import bucket, first
from notion_database_ai.row import Row


async def update_rows(
    rows: list[Row],
    database_id: str,
):
    # - Init notion client

    client = NotionRateLimitedClient(auth=Deps.load().config.notion_token)

    # - Prefetch all properties

    await asyncio.gather(*([prefetch_all_cached_properties(row) for row in rows]))

    # - Update notion pages

    await client.upsert_database(
        database={"id": database_id},
        pages=await asyncio.gather(*[row.notion_page for row in rows]),
        page_unique_id_func=lambda page: page["properties"]["name"]["title"][0]["text"]["content"],
        remove_others=False,
    )


# fmt: off

def test():
    databases_list = [
        "MySQL",
        "PostgreSQL",
        "Oracle Database",
        "Microsoft SQL Server",
        "MariaDB",
        "IBM Db2",
        "SQLite",
        "Amazon Aurora",
        "CockroachDB",
        "Greenplum",
        "Exadata",
        "TiDB",
        "VoltDB",
        "Google Cloud SQL",
        "Amazon RDS",
        "Snowflake",
        "Teradata",
        "MongoDB",
        "Cassandra",
        "Couchbase",
        "Amazon DynamoDB",
        "HBase",
        "Redis",
        "Neo4j",
        "Firebase Realtime Database",
        "ArangoDB",
        "RocksDB",
        "FoundationDB",
        "RethinkDB",
        "OrientDB",
        "Aerospike",
        "Amazon DocumentDB",
        "MarkLogic",
        "AllegroGraph",
        "CouchDB",
        "FaunaDB",
        "YugabyteDB",
        "ScyllaDB",
        "Titan",
        "RavenDB",
        "JanusGraph",
        "Memcached",
        "Hazelcast",
        "KeyDB",
        "TiKV",
        "EventStore",
        "InfluxDB",
        "Prometheus",
        "TimescaleDB",
        "Graphite",
        "OpenTSDB",
        "Druid",
        "VictoriaMetrics",
        "QuestDB",
        "ClickHouse",
        "Google BigQuery",
        "Amazon Redshift",
        "Azure Synapse Analytics",
        "Vertica",
        "Parquet",
        "Kudu",
        "Apache Pinot",
        "HyPer",
        "TigerGraph",
        "Amazon Neptune",
        "etcd",
        "Riak",
        "LevelDB",
        "Berkeley DB",
        "Db4o",
        "ObjectDB",
        "Versant Object Database",
        "Microsoft Azure Cosmos DB",
        "H2 Database",
        "Realm",
        "Google Spanner",
        "Citus",
        "Elasticsearch",
        "Solr",
        "Splunk",
        "Algolia",
        "Sphinx",
        "MeiliSearch",
        "Typesense",
        "Ignite",
        "VelocityDB",
        "Tarantool",
        "IBM Db2 on Cloud",
        "Oracle Autonomous Database",
        "MongoDB Atlas",
        "Firebase Firestore",
        "Hadoop",
        "Apache Hive",
        "Apache Spark",
        "Apache Flink",
        "Presto",
        "Apache Kafka",
        "Google Bigtable",
        "Amazon EMR",
        "MapR",
        "Cloudera",
        "Hortonworks",
        "NuoDB",
        "MemSQL (SingleStore)",
        "FoundationDB",
        "IBM Db2 Federation",
        "Microsoft Azure SQL Data Warehouse",
        "Teradata QueryGrid",
        "BaseX",
        "eXist-db",
        "Sedna",
        "PostGIS",
        "Oracle Spatial",
        "GeoMesa",
        "Neo4j with Spatial",
        "Google BigQuery GIS",
        "Hyperledger Fabric",
        "Ethereum",
        "Corda",
        "Quorum",
        "BigchainDB",
        "IBM Db2 Warehouse",
        "MLDB (Machine Learning Database)",
        "Google BigQuery ML",
        "FlinkML",
        "EventStoreDB",
        "Amazon Kinesis",
        "NATS Streaming",
        "Pulsar",
        "LDAP",
        "Active Directory",
        "OpenLDAP",
        "Apache Directory",
        "Firebird Embedded",
    ]

    async def main():
        await update_rows(
            database_id="dfe5de58b8c34bce9a30db8448dcf5d5",
            rows=[Row(name=name) for name in databases_list]
            # rows=[Row(name=name) for name in ['Google BigQuery']]
        )

    import asyncio

    asyncio.run(main())


# fmt: on

if __name__ == "__main__":
    test()
