# Multi-Environment Deployment Manager

## 1. Project Overview
The **Multi-Environment Deployment Manager** is a production-style DevOps project designed to demonstrate automated deployments across development, staging, and production environments. It showcases how a single, reproducible build artifact can be deployed with different configurations depending on the target environment, embodying key principles of modern software delivery.

## 2. Architecture
The project follows a standard CI/CD workflow:

**Developer** → **GitHub** → **CI/CD Pipeline** → **Docker Containers** → **Environments**

1. Code changes are pushed to the GitHub repository.
2. The CI/CD pipeline intercepts the push, running linting and building the Docker image.
3. The resulting Docker image is run as containers across the different environments (Dev, Staging, Prod).

## 3. Tech Stack
This project leverages the following technologies:
- **Python / Flask**: The core web application framework.
- **Docker**: For containerizing the application.
- **Docker Compose**: For orchestrating the multi-environment setup locally.
- **GitHub Actions**: For the Continuous Integration and Continuous Deployment (CI/CD) pipeline.
- **Kubernetes**: For production-grade container orchestration.

## 4. Project Structure
```text
.
├── .github/
│   └── workflows/
│       └── cicd.yml           # CI/CD Pipeline definition for GitHub Actions.
├── infrastructure/
│   └── kubernetes/
│       ├── deployment.yaml    # Defines the Kubernetes Deployment (replicas, image, etc.).
│       └── service.yaml       # Defines the Kubernetes Service to expose the application.
├── monitoring/
│   └── README.md              # Documentation placeholder for monitoring solutions.
├── src/
│   └── app.py                 # The main Flask application source code.
├── .env                       # Base environment variables file.
├── docker-compose.yml         # Local orchestration for dev, staging, and prod environments.
├── Dockerfile                 # Instructions for building the application's Docker image.
└── requirements.txt           # Python dependency list.
```

## 5. Installation
To run this project locally, clone the repository and use Docker Compose:

```bash
git clone <repository-url>
cd "Multi-Environment Deployment Manager"
docker-compose up --build
```

## 6. Usage
Once the containers are running via Docker Compose, you can access the application's different environments on their respective ports. Each environment runs the exact same code but behaves differently based on injected environment variables.

- **Development**: [http://localhost:8080/](http://localhost:8080/)
- **Staging**: [http://localhost:8081/](http://localhost:8081/)
- **Production**: [http://localhost:8082/](http://localhost:8082/)

*Note: You can also verify the health of each service by visiting `/health` on any of these ports.*

## 7. CI/CD Pipeline
The automated build process is defined in `.github/workflows/cicd.yml`. It is triggered automatically on pushes and pull requests to the `main` branch. The pipeline:
1. Checks out the source code.
2. Sets up the Python environment.
3. Installs necessary dependencies.
4. Runs `flake8` to enforce code quality and linting standards.
5. Builds the Docker image (`devopsproject:latest`).
6. Prints a success message upon completion.

## 8. Kubernetes Deployment
For production scale, this project includes Kubernetes manifests in the `infrastructure/kubernetes/` directory:
- **`deployment.yaml`**: Ensures that 2 replicas of the `devopsproject:latest` container are running for high availability, labeling them as `app: devops-app`.
- **`service.yaml`**: Exposes the deployment using a LoadBalancer on port `8080`, routing incoming traffic to the appropriate pods.

## 9. Monitoring
The `monitoring/` directory contains a placeholder explaining how to implement monitoring for this application. It details how tools like **Nagios** or **Prometheus** can be used to track:
- Container health (via the `/health` endpoint).
- CPU and Memory usage.
- Request latency and traffic patterns.

## 10. Learning Outcomes
By exploring this project, you will gain hands-on experience with:
- **DevOps automation**: Linking code changes to automated builds.
- **Container orchestration**: Managing multiple environments with Docker Compose and scaling with Kubernetes.
- **CI/CD workflows**: Implementing automated linting and image building using GitHub Actions.
