# Docker-Based AI Configuration Management System

## Overview
This project was developed as a **take-home technical case study**
during an internship interview process.

The goal of the project is to provide a local, containerized system
that allows users to update application configuration values using
**natural language commands**, without directly editing JSON files.

No proprietary or confidential company information is included.

---

## System Architecture
The system consists of three independent services, each running in its
own Docker container:

### Schema Service
- Serves JSON Schemas for applications
- Defines allowed structure, fields, and constraints

### Values Service
- Serves the current configuration values of applications
- Keeps configuration values separate from schemas

### Bot Service
- Accepts natural language user input
- Uses a **local LLM (via Ollama)** to understand the request
- Validates and applies configuration changes according to JSON Schema

---

## Technologies Used
- Python
- Docker & Docker Compose
- JSON Schema
- Local LLM (Ollama)

---

## How to Run
Start the entire system with a single command:

```bash
docker compose up
