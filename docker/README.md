## Development Environment Setup

**Requirements:**
- Docker Compose 1.12.0+ (`docker-compose version`)
- Docker API 1.25+ (`docker version`)
- Git

Note: You will also need to append nginx to your 127.0.0.1 entry in `/etc/hosts`.

```bash
##
# Host Database
#
# localhost is used to configure the loopback interface
# when the system is booting.  Do not change this entry.
##
127.0.0.1       localhost nginx
255.255.255.255 broadcasthost
::1             localhost
```

The reason for this is due to osgeo_importer. It uses gsconfig which parses `workspace_style_url` from geoserver rest 
xml atom:link, which uses the entry from global.xml. Since each application is in separate containers, localhost will 
not work as that value. To bypass this the nginx service alias `nginx` is used. If added to youe `/etc/hosts` it will 
resolve as localhost.

#### Clone Repo
There are two submodules in the vendor directory
- geonode
- maploom

Run the following command to clone all repositories

```bash
git clone --recursive -j8 git://github.com/boundlessgeo/exchange.git
cd exchange
```

#### Update Repo
```bash
cd exchange
git submodule update --init --recursive
```

#### Initial Docker Setup
This will run all the docker containers and display log output in the terminal

```bash
docker-compose up
```

Note: To run in detached mode append a `-d` to the above. This will not display the log output in the terminal.
If you want access to the logs for a specific container then you will need to run the following command:
```bash
docker-compose logs -f exchange
```

**IMPORTANT:** If you you run the following:
```bash
docker-compose down
docker-compose restart
```
All data will persist due to the named volumes. If you are wanting to start from a clean slate. You will need 
to do the following:
```bash
docker-compose down
docker volume prune # add `-f` to bypass the prompt
docker-compose up
```
To display the volumes run the following:
```bash
docker volume ls
```
Example output:
```bash
DRIVER              VOLUME NAME
local               0ce98919212c546e67e4c48e09bb595612143a5a8d386c55f17ed0287e8c2e0c # random volume created for nginx
local               exchange_db_data
local               exchange_django_media
local               exchange_geoserver_data
local               exchange_queue_data
local               exchange_search_data
```

Additional Online References:
- [docker-compose up](https://docs.docker.com/compose/reference/up/)
- [docker-compose build](https://docs.docker.com/compose/reference/build/)
- [docker-compose down](https://docs.docker.com/compose/reference/down/)
- [docker-compose ps](https://docs.docker.com/compose/reference/ps/)
- [docker-compose exec](https://docs.docker.com/compose/reference/exec/)
- [docker volume](https://docs.docker.com/engine/reference/commandline/volume/)

#### Development Attached Volume
There are two volumes used in the development setup

1. $PWD:/code:ro

The first one mounts the exchange directory including submodules in the `/code` directory for the `exchange`
container. `:rw` is required in order to run tests and coverage.

#### Settings
Docker reads from two areas for settings in this environment.

1. .env
2. docker-compose:environment:

The first one id where you may need to make adjustments. The second should not require any changes. The only
containers that utilize the `.env` file are exchange, registry and worker.

**Note:** In the `.env` file you will see a `DEV=1` entry. The exchange/worker Dockerfile will install geonode from 
the vendor/geonode submodule if it has any value. Placing a `DEV=` will install geonode from the 
`requirements.txt` entry.

#### Running Tests and Coverage
```bash
docker-compose exec exchange /bin/bash -c /code/docker/exchange/run_tests.sh
```
Output will be in 2 files:

1. `docker/data/pytest-results.xml` - pytest results
2. `docker/data/coverage.xml` - coverage results

To run pycodestyle and yamllint run the following command:

```bash
docker run -v $PWD:/code \
           -w /code quay.io/boundlessgeo/sonar-maven-py3-alpine bash \
           -e -c 'ls -las && . docker/devops/helper.sh && lint'
```

**Note:** `$PWD` is `exchange` root directory

#### Questions
If you have any questions feel free to reach out in the following `Boundless` slack channels:

- `#exchange-dev` Exchange Development Team
- `#qa-deployment` Exhange QA/Deployment (CI)
