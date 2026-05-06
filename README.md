# Calculation Cycle Backend

## Overview

This is the backend component of the Calculation Cycle Plugin for the iLens 2.0 platform. It provides RESTful APIs for calculation cycle management, process order handling, and dashboard data retrieval.

## Features

- FastAPI-based microservice
- Time calculation engine for production cycles
- Integration with MongoDB and PostgreSQL
- Process order management
- Dashboard data services

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Configure application.conf and environment variables
3. Run: `python main.py`

## API Documentation

Available at `/docs` when running the server.

## Structure

- `app.py`: Main application entry point
- `main.py`: Server startup
- `scripts/core/`: Core business logic
- `scripts/db/`: Database utilities
- `scripts/handlers/`: Request handlers
- `scripts/services/`: API services
