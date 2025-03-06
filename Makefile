.PHONY: build deploy remove load all

build:
	docker build --target application -t application:latest .
	docker build --target worker -t worker:latest .

load:
	minikube image load application:latest
	minikube image load worker:latest

deploy:
	kubectl apply -f deployment.yaml

remove:
	kubectl delete -f deployment.yaml
	
all: build load
