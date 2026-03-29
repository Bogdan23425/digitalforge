import os
from time import sleep

import psycopg


def main() -> None:
    dbname = os.getenv("POSTGRES_DB", "digitalforge")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    port = os.getenv("POSTGRES_PORT", "5432")
    conninfo = (
        f"dbname={dbname} user={user} password={password} " f"host={host} port={port}"
    )
    while True:
        try:
            psycopg.connect(conninfo).close()
            break
        except psycopg.OperationalError:
            sleep(1)


if __name__ == "__main__":
    main()
