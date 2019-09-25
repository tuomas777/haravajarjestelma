# Haravajärjestelmä

:fallen_leaf: API for volunteer work events :fallen_leaf:

## Development with Docker

1. Create `.env` environment file

2. Set the `DEBUG` environment variable to `1`

3. Run `docker-compose up`

4. Run migrations if needed: 
    * `docker exec haravajarjestelma python manage.py migrate`

5. Create superuser if needed: 
    * `docker exec -it haravajarjestelma python manage.py createsuperuser`

6. Import geo data
    * `docker exec -it haravajarjestelma python manage.py geo_import --municipalities finland`
    * `docker exec -it haravajarjestelma python manage.py geo_import --divisions helsinki`
    * `docker exec -it haravajarjestelma python manage.py geo_import --addresses helsinki`
    * `docker exec -it haravajarjestelma python manage.py import_helsinki_contract_zones`

The project is now running at [localhost:8000](http://localhost:8000)

## Development without Docker

### Install pip-tools

* Run `pip install pip-tools`

### Creating Python requirements files

* Run `pip-compile requirements.in`

### Updating Python requirements files

* Run `pip-compile --upgrade requirements.in`

### Installing Python requirements

* Run `pip-sync requirements.txt`

### Database

To setup a database compatible with default database settings:

Create user and database

    sudo -u postgres createuser -P -R -S haravajarjestelma  # use password `haravajarjestelma`
    sudo -u postgres createdb -O haravajarjestelma haravajarjestelma
    
Create extensions in the database
    
    sudo -u postgres psql haravajarjestelma -c "CREATE EXTENSION postgis;"

Allow user to create test database

    sudo -u postgres psql -c "ALTER USER haravajarjestelma CREATEDB;"

Run migrations if needed:

    python manage.py migrate

Create superuser if needed:

    python manage.py createsuperuser

Import geo data

    python manage.py geo_import --municipalities finland
    python manage.py geo_import --divisions helsinki
    python manage.py geo_import --addresses helsinki
    python manage.py import_helsinki_contract_zones

### Daily running

* Set the `DEBUG` environment variable to `1`.
* Run `python manage.py migrate`
* Run `python manage.py runserver 0:8000`

The project is now running at [localhost:8000](http://localhost:8000)

## Code format

This project uses [`black`](https://github.com/ambv/black) for Python code formatting.
We follow the basic config, without any modifications. Basic `black` commands:

* To let `black` do its magic: `black .`
* To see which files `black` would change: `black --check .`
