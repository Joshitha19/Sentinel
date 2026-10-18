.PHONY: help install backend frontend test docker run

help:
	@echo "SENTINEL commands:"
	@echo "  make install    - Install Python and Node dependencies"
	@echo "  make backend    - Start FastAPI backend (http://localhost:8000)"
	@echo "  make frontend   - Start React frontend (http://localhost:5173)"
	@echo "  make test       - Run backend unit tests"
	@echo "  make docker     - Run full stack with docker-compose"

install:
	pip install -r backend/requirements.txt
	cd frontend && npm install

backend:
	cd backend && python run_backend.py

frontend:
	cd frontend && npm run dev

test:
	python backend/tests/run_tests.py

docker:
	docker-compose up --build
