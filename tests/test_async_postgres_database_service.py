from src.services.async_postgres_database_service import AsyncPostgresDatabaseService


def test_build_connect_args_for_pooler_url():
    service = AsyncPostgresDatabaseService(
        "postgresql://user:pass@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"
    )

    connect_args = service._build_connect_args()

    assert connect_args["statement_cache_size"] == 0
    assert connect_args["prepared_statement_cache_size"] == 0
    assert callable(connect_args["prepared_statement_name_func"])
    assert (
        connect_args["prepared_statement_name_func"]()
        != connect_args["prepared_statement_name_func"]()
    )


def test_build_connect_args_for_direct_postgres_url():
    service = AsyncPostgresDatabaseService(
        "postgresql://user:pass@db.example.com:5432/postgres"
    )

    connect_args = service._build_connect_args()

    assert connect_args["statement_cache_size"] == 0
    assert connect_args["prepared_statement_cache_size"] == 0
    assert "prepared_statement_name_func" not in connect_args
