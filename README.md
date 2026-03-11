# Multi-Environment Deployment Manager

A minimal but production-style DevOps project demonstrating key DevOps principles including multi-environment configuration, containerization, CI/CD, orchestration, and monitoring.

## Project Structure

This project is organized to showcase a standard DevOps lifecycle:

```
.
├── .github/
│   └── workflows/
│       └── cicd.yml           # CI/CD Pipeline: Automates testing, linting, and Docker image builds on push/PR.
├── infrastructure/
│   └── kubernetes/
│       ├── deployment.yaml    # Container Orchestration: Defines the desired state (2 replicas) for high availability.
│       └── service.yaml       # Networking: Exposes the deployment to handle incoming traffic on port 8080.
├── monitoring/
│   └── README.md              # Observability: Documentation on how to monitor health, CPU, and latency.
├── src/
│   └── app.py                 # Application Code: A simple Flask API with a / health check endpoint.
├── .env                       # Environment Variables: Base configuration (empty by default).
├── docker-compose.yml         # Local Environment Management: Spins up dev, staging, and prod simultaneously.
├── Dockerfile                 # Containerization: Packages the Flask app and its dependencies into a reproducible image.
└── requirements.txt           # Dependency Management: Pins Python dependencies (Flask) for consistent builds.
```

## How to Run Locally

You can run this project locally using Docker Compose, which will spin up three separate environments (Development, Staging, Production) simultaneously from the exact same Docker image, demonstrating the principle of **build once, deploy anywhere**.

1. Ensure Docker Desktop is running.
2. Run the following command in the project root:

```bash
docker-compose up --build
```

Access the environments at:
- **Dev**: [http://localhost:8000/](http://localhost:8000/) *(Port changed from 8080 to avoid conflicts)*
- **Staging**: [http://localhost:8081/](http://localhost:8081/)
- **Prod**: [http://localhost:8082/](http://localhost:8082/)

Check the health endpoints (e.g., [http://localhost:8000/health](http://localhost:8000/health)).

## DevOps Principles Demonstrated

1. **Configuration Management / Environment Parity:** The `app.py` behaves differently based on the `APP_ENV` environment variable, while using the exact same underlying `devopsproject:latest` image.
2. **Infrastructure as Code (IaC):** The Kubernetes `.yaml` files define the infrastructure declaratively.
3. **Continuous Integration / Continuous Deployment (CI/CD):** GitHub Actions automatically lint the code and build the image whenever changes are made to the `main` branch.
4. **Observability:** The `/health` endpoint and monitoring documentation provide a foundation for understanding application state in production.
