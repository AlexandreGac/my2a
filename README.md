# My2A

Useful website to manage student application form at the begining of the 2nd year at Ecole des Ponts ParisTech

## Installation [DEV]

/!\ As CAS authentication is not possible on localhost, you could have some troubles when launching the website for the first time. (Multiple re-renders, browser lags...). To avoid that, make sure to follow carefully step 5 and 6. 

To install and run this project for a development environment, follow these steps:

1. Clone the repository:

    ```shell
    git clone https://github.com/adcrry/my2a
    ```

2. Setup environment variables (edit .env file if needed)

    ```shell
    cp .env-example .env
    ```

3. Build images

    ```shell
    docker compose build
    ```

4. Run 

    ```shell
    docker compose up
    ```

5. Create an admin account to access the website without CAS. 

    ```shell
    docker exec -it my2a-back-1 python manage.py createsuperuser
    ```

Be careful: the container name 'my2a-back-1' can be different. If it doesn't work, see 'docker ps' and get the proper container name.  

6. Open your web browser and visit `http://localhost/admin/` (the last / is very important !!!!! Do not forget it !!) to login with previous credentials.

7. Visit `http://localhost/`.

## Production

1. Clone the repository:

    ```shell
    git clone https://github.com/adcrry/my2a
    ```

2. Setup environment variables (edit .env file if needed)

    ```shell
    cp .env-example .env
    ```

3. Build images

    ```shell
    docker compose build
    ```

4. Run 

    ```shell
    docker compose up
    ```

5. Populate the database with courses, departments, parcours etc. 

6. Do not forget to setup a reverse proxy that redirect my2a.enpc.org to the my2a's proxy.

NB :
- Login: root | rootGI
- passw: a | abababab