#iTicket

####DRF driven ticket system with token based auth, FSM, swagger but without Black Jack and etc.

### Installation
    
    $ git clone https://github.com/rlikhachev/iTicket
    $ cd iTicket
    $ cp .env.sample ./.env
    $ docker-compose up -d
    
### Restore base from example dump.sql 
    
    $ docker exec -i -t iticket_db_1 sh 
    # psql -U base
    ~ # CREATE USER postgres WITH SUPERUSER LOGIN
    ~ # \q
    # su postgres -c "dropdb base && createdb base && psql base < /dumps/dump.sql"
    # exit

### Testing
    
    $ docker exec -i -t iticket_django_1 sh
    # python manage.py test
    # exit
