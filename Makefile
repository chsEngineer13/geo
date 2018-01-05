SHELL:=bash
mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
current_dir := $(dir $(mkfile_path))

.PHONY: help html lint start purge stop recreate test

help:
	@echo "  make lint     - run to lint (style check) repo"
	@echo "  make html     - build sphinx documentation"
	@echo "  make start    - start containers"
	@echo "  make stop     - stop containers"
	@echo "  make purge    - stop containers and prune volumes"
	@echo "  make recreate - stop containers, prune volumes and recreate/build containers"
	@echo "  make test     - run unit tests"

html:
	@docker run -v $(current_dir):/code \
                -w /code quay.io/boundlessgeo/bex-py27-stretch bash \
                -e -c 'python setup.py build_sphinx'

lint:
	@docker run -v $(current_dir):/code \
                -w /code quay.io/boundlessgeo/sonar-maven-py3-alpine bash \
                -e -c '. docker/devops/helper.sh && lint'

stop:
	@docker-compose down --remove-orphans

start: stop
	@docker-compose up -d --build

purge: stop
	@docker volume prune -f

recreate: purge
	@docker-compose up -d --build --force-recreate

test:
	@echo "Note: test requires the exchange container to be running and healthy"
	@docker-compose exec exchange /code/docker/exchange/run_tests.sh
