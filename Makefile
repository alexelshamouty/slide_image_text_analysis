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
	minikube image rm application:latest || true
	docker build -t application:latest -f Dockerfile.application .
	minikube image load application:latest
	kubectl apply -f deployment.yaml

rebuild-worker:
	kubectl delete deployment analyzer-worker || true
	minikube image rm worker:latest || true
	docker build -t worker:latest -f Dockerfile.worker .
	minikube image load worker:latest
	kubectl apply -f deployment.yaml

rebuild-backend:
	kubectl delete deployment backend-api || true
	minikube image rm backend:latest || true
	docker build -t backend:latest -f Dockerfile.backend .
	minikube image load backend:latest
	kubectl apply -f deployment.yaml
