from time import sleep

import psycopg


def main() -> None:
    while True:
        try:
            psycopg.connect(
                "dbname=digitalforge user=postgres password=postgres host=127.0.0.1 port=5432"
            ).close()
            break
        except psycopg.OperationalError:
            sleep(1)


if __name__ == "__main__":
    main()
