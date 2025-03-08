.PHONY: removeimages build deploy remove load all rebuild-backend rebuild-worker rebuild-webapi

build:
	docker build --target backend -t backend:latest .
	docker build --target worker -t worker:latest .
	docker build --target api -t api:latest .

load:
	parallel minikube image load ::: backend:latest worker:latest api:latest

removeimages:
	parallel minikube image rm ::: backend:latest worker:latest api:latest

deploy:
	kubectl apply -f deployment.yaml

remove:
	kubectl delete -f deployment.yaml
	
all: build load

rebuild-backend:
	kubectl delete deployment analyzer-backend || true
	sleep 60
	minikube image rm backend:latest || true
	docker build --target backend -t backend:latest  . || true
	minikube image load backend:latest || true
	kubectl apply -f deployment.yaml || true

rebuild-worker:
	kubectl delete deployment analyzer-worker || true
	sleep 60
	minikube image rm worker:latest || true
	docker build --target worker -t worker:latest  . || true
	minikube image load worker:latest || true
	kubectl apply -f deployment.yaml || true

rebuild-webapi:
	kubectl delete deployment web-api || true
	sleep 60
	minikube image rm api:latest || true
	docker build --target api -t api:latest. || true
	minikube image load api:latest || true
	kubectl apply -f deployment.yaml || true
