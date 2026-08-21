# ORBIT-X Master Production Makefile

.PHONY: help install test test-backend test-workers benchmark dev docker-build docker-up docker-down k8s-apply k8s-delete

help:
	@echo "ORBIT-X Production Management Commands:"
	@echo "  make install        Install Python and Node.js worker dependencies"
	@echo "  make test           Run all Python and Node.js tests (79 tests)"
	@echo "  make test-backend   Run Python backend pytest suite (74 tests)"
	@echo "  make test-workers   Run Node.js BullMQ worker tests (5 tests)"
	@echo "  make benchmark      Execute reproducible production benchmarks"
	@echo "  make docker-build   Build production Docker container images"
	@echo "  make docker-up      Launch multi-service production stack with Docker Compose"
	@echo "  make docker-down    Tear down Docker Compose stack"
	@echo "  make k8s-apply      Deploy complete stack to Kubernetes (k8s/)"
	@echo "  make k8s-delete     Delete Kubernetes namespace and resources"

install:
	cd backend && uv pip install -e .
	cd workers && npm install
	cd frontend && npm install

test: test-backend test-workers

test-backend:
	cd backend && .venv/Scripts/pytest tests/

test-workers:
	cd workers && npm test

benchmark:
	cd backend && .venv/Scripts/python scripts/run_production_benchmarks.py

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down -v

k8s-apply:
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/configmap.yaml
	kubectl apply -f k8s/secrets.yaml
	kubectl apply -f k8s/redis/
	kubectl apply -f k8s/postgres/
	kubectl apply -f k8s/kafka/
	kubectl apply -f k8s/worker/
	kubectl apply -f k8s/api/
	kubectl apply -f k8s/hpa.yaml
	kubectl apply -f k8s/ingress.yaml

k8s-delete:
	kubectl delete namespace orbitx
