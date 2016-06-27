.PHONY: registry
registry:
	echo "Creating registry services"
	cf create-service elephantsql turtle registry-database
	cf create-service searchly starter registry-elasticsearch
	cf create-service cloudamqp lemur registry-rabbitmq
	cf push -f cf/manifest.yml

.PHONY: registry-clean
registry-clean:
	cf delete registry-test -f
	cf delete registry-celery -f
	cf delete-service registry-database -f
	cf delete-service registry-elasticsearch -f
	cf delete-service registry-rabbitmq -f

.PHONY: exchange
exchange:
	echo "Creating exchange services"
	cf create-service elephantsql turtle exchange-database
	cf create-service searchly starter exchange-elasticsearch
	cf create-service cloudamqp lemur exchange-rabbitmq
	cf push -f cf/manifest.yml

.PHONY: exchange-clean
exchange-clean:
	cf delete exchange-test -f
	cf delete exchange-celery -f
	cf delete-service exchange-database -f
	cf delete-service exchange-elasticsearch -f
	cf delete-service exchange-rabbitmq -f	