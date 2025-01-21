from django.db import connection

maintenance_queries = {
    "vacuum": {
        "description": "Reclaims storage and optimizes database performance.",
        "query": "VACUUM VERBOSE;",
    },
    "vacuum_analyze": {
        "description": "Reclaims storage and updates statistics for better query planning.",
        "query": "VACUUM ANALYZE VERBOSE;",
    },
    "reindex_table": {
        "description": "Rebuilds indexes for a specific table (useful for a specific table with heavy updates).",
        "query": lambda table_name: f"REINDEX TABLE {table_name};",
    },
    "analyze": {
        "description": "Updates statistics to help PostgreSQL make better query planning decisions.",
        "query": lambda table_name: f"ANALYZE {table_name};",
    },
    "vacuum_full": {
        "description": "Reclaims storage and compacts tables by writing a new copy of the table to disk (more intensive).",
        "query": lambda table_name: f"VACUUM FULL {table_name};",
    },
}


def run_custom_sql(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        if query.strip().lower().startswith("select"):
            result = cursor.fetchall()
            if not result:
                print("No results returned.")
                return None
            return result
        else:
            affected_rows = cursor.rowcount
            print(f"{affected_rows} rows affected.")
            return affected_rows
