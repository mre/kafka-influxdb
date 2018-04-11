
# e.g. make up RUNTIME (py2, py3 or pypy)
RUNTIME=py2

.PHONY: test
test:
	python setup.py test

.PHONY: all
all: clean up

.PHONY: up
up:
	docker-compose -f docker/common-services.yml -f docker/${RUNTIME}/docker-compose.yml build
	docker-compose -f docker/common-services.yml -f docker/${RUNTIME}/docker-compose.yml up -d --force-recreate

.PHONY: stop
stop:
	docker-compose -f docker/common-services.yml -f docker/${RUNTIME}/docker-compose.yml stop

.PHONY: down
down:
	docker-compose -f docker/common-services.yml -f docker/${RUNTIME}/docker-compose.yml down

.PHONY: logs
logs:
	docker-compose -f docker/common-services.yml -f docker/${RUNTIME}/docker-compose.yml logs

.PHONY: stats
stats:
	docker-compose -f docker/common-services.yml -f docker/${RUNTIME}/docker-compose.yml logs kafkainfluxdb

.PHONY: messages
messages:
	docker-compose -f docker/common-services.yml up kafkacat

.PHONY: clean
clean:
	docker-compose -f docker/common-services.yml -f docker/${RUNTIME}/docker-compose.yml kill
	docker-compose -f docker/common-services.yml -f docker/${RUNTIME}/docker-compose.yml rm -f

.PHONY: help
help:
	@echo "Command                     Description"
	@echo "make                        docker-compose up"
	@echo "make up                     docker-compose up"
	@echo "make stop                   docker-compose stop"
	@echo "make down                   docker-compose down"
	@echo "make logs                   docker-compose logs"
	@echo "make stats                  docker-compose logs kafkainfluxdb"
	@echo "make messages               Create sample messages for benchmark"
	@echo "make clean                  docker-compose clean && docker-compose rm -f"
	@echo "make <cmd> RUNTIME=<env>    Choose runtime environment (py2, py3, pypy or logstash). Default: py2"
