.PHONY: removeimages build deploy remove load all rebuild-application rebuild-worker rebuild-backend

build:
	docker build --target application -t application:latest .
	docker build --target worker -t worker:latest .
	docker build --target backend -t backend:latest .

load:
	parallel minikube image load ::: application:latest worker:latest backend:latest

removeimages:
	parallel minikube image rm ::: application:latest worker:latest backend:latest

deploy:
	kubectl apply -f deployment.yaml

remove:
	kubectl delete -f deployment.yaml
	
all: build load

rebuild-application:
	kubectl delete deployment analyzer-application || true
	sleep 60
	minikube image rm application:latest || true
	docker build --target application -t application:latest  . || true
	minikube image load application:latest || true
	kubectl apply -f deployment.yaml || true

rebuild-worker:
	kubectl delete deployment analyzer-worker || true
	sleep 60
	minikube image rm worker:latest || true
	docker build --target worker -t worker:latest  . || true
	minikube image load worker:latest || true
	kubectl apply -f deployment.yaml || true

rebuild-backend:
	kubectl delete deployment backend-api || true
	sleep 60
	minikube image rm backend:latest || true
	docker build --target backend -t backend:latest. || true
	minikube image load backend:latest || true
	kubectl apply -f deployment.yaml || true
