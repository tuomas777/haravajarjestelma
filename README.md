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

### Daily running

* Set the `DEBUG` environment variable to `1`.
* Run `python manage.py migrate`
* Run `python manage.py runserver 0:8000`

The project is now running at [localhost:8000](http://localhost:8000)
