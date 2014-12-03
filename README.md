Pokr - Politics in Korea
==================================

**Pull requests are always welcome.**

## Installation

1. Install dependencies

    - Install [node.js](http://nodejs.org/)
    - Ubuntu

            $ apt-get install postgresql-9.3 npm python-psycopg2 node-less node-uglify
            $ pip install -r requirements.txt
            $ make install

    - Mac OS X

            $ brew install postgresql
            $ npm install less uglify-js -g
            $ pip install -r requirements.txt
            $ pip install psycopg2
            $ make install

1. Create & modify configuration files

        $ make init
        $ createuser postgres
    - Set password for user "postgres" in PostgreSQL
    - Modify `alembic.ini`
        - `ID_HERE`: postgres id (ex: postgres)
        - `PASSWD_HERE`: postgres pw
        - `HOST_HERE`: postgres host (ex: localhost)

1. Create & init DB (You should first obtain a `pokrdb.dump` from the admins: contact@popong.com) 

        $ sudo -u postgres psql -h localhost -U postgres -c 'CREATE DATABASE pokrdb;'
        $ sudo -u postgres psql -d pokrdb -f pokrdb.dump
        $ ./shell.py db init
        $ alembic stamp head

## Run Server

    $ ./run.py [-d] [-l LOCALE] [--port PORT]

## Update Data

1. Bills

        $ ./shell.py bill update "some/where/*.json" # from files
        $ ./shell.py bill update --source redis  # from Redis queue
        $ ./shell.py bill update --source db  # existing bills of the current session

1. Bill Keywords

        $ ./shell.py bill_keyword update "some/where/*.txt"

1. Candidacies

        $ ./shell.py candidacy update "some/where/*.json"

## License
[Apache v2.0](http://www.apache.org/licenses/LICENSE-2.0.html)
