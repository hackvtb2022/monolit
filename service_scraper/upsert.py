from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert


def compile_query(query):
    compiler = (
        query.compile if not hasattr(query, "statement") else query.statement.compile
    )
    return compiler(dialect=postgresql.dialect())


def upsert(session, model, rows, as_of_date_col="report_date", no_update_cols=[]):
    table = model.__table__

    stmt = insert(table).values(rows)

    update_cols = [
        c.name
        for c in table.c
        if c not in list(table.primary_key.columns) and c.name not in no_update_cols
    ]

    on_conflict_stmt = stmt.on_conflict_do_update(
        index_elements=table.primary_key.columns,
        set_={k: getattr(stmt.excluded, k) for k in update_cols},
        index_where=(
            getattr(model, as_of_date_col) < getattr(stmt.excluded, as_of_date_col)
        ),
    )

    session.execute(on_conflict_stmt)
