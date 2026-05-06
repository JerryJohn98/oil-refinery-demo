# Calculation Cycle Plugin

## Overview

The Calculation Cycle Plugin is a microservice component designed for the iLens 2.0 platform, specifically tailored for PepsiCo's paperless dashboard solutions. This plugin enables the calculation and visualization of production metrics based on specific calculation cycles, such as post-changeover and post-maintenance periods.

## Features

- **Calculation Cycles**: Supports two primary calculation cycles:
  - Post Changeover: Calculates metrics after equipment changeover events
  - Post Maintenance: Calculates metrics following maintenance activities

- **Process Order Management**: Fetches and manages process orders (POs) relevant to the selected calculation cycle and time range

- **Time Range Calculations**: Advanced time filtering with support for:
  - Custom date ranges
  - Predefined time periods (e.g., last N days, weeks, months)
  - Timezone-aware calculations
  - Shift-based filtering

- **Dashboard Integration**: Provides dropdown filters and data for dashboard widgets, including:
  - Hierarchy-based filtering (lines, plants, etc.)
  - Ongoing production plan tracking
  - Real-time data visualization

- **Multi-Database Support**: Integrates with multiple data sources:
  - MongoDB for configuration and hierarchy data
  - PostgreSQL for production, OEE, and event data

## Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with automatic API documentation
- **Core Components**:
  - Time Calculator Engine: Handles complex time range computations
  - Handlers: Business logic for dashboard and PO operations
  - Services: API endpoints for frontend integration
  - Database Utilities: Abstraction layer for MongoDB and PostgreSQL interactions

### Frontend (Angular)
- **Framework**: Angular 12 with TypeScript
- **UI Components**: Bootstrap-based responsive interface
- **Features**: Date/time pickers, dropdowns, and data visualization

## API Endpoints

- `GET /visualization/healthcheck`: Service health check
- Dashboard services for PO fetching and hierarchy data
- Calculation cycle dropdown data retrieval

## Installation and Setup

### Prerequisites
- Python 3.10+
- Node.js 14+
- Docker (for containerized deployment)
- Access to required databases (MongoDB, PostgreSQL)

### Backend Setup
1. Navigate to the `backend` directory
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables in `.env` file
4. Run the application: `python app.py`

### Frontend Setup
1. Navigate to the `frontend` directory
2. Install dependencies: `npm install`
3. Build the application: `npm run build`
4. Serve the built files via the backend static files mount

### Docker Deployment
- Backend Dockerfile provided for containerized deployment
- Compatible with iLens 2.0 plugin architecture

## Configuration

- **Application Config**: `backend/conf/application.conf`
- **Logging**: `backend/scripts/logging/logger_conf.yml`
- **Widget Config**: `backend/assets/widgetConfig.json`

## Development

### Running Tests
- Backend: Use pytest for unit tests
- Frontend: `npm test` for Angular tests

### Building
- Backend: No build step required for Python
- Frontend: `npm run build` for production build

## Contributing

This plugin is part of the iLens 2.0 ecosystem. For contributions, please follow the standard KnowledgeLens development guidelines.

## Detailed Documentation
https://rockwellautomation.sharepoint.com/:w:/s/DiageoProjectBedrock/IQAnUz8BjBFSRZOyXWy7O9b8AXmbzXW0PzohLBMM1vNZd9w?email=Jasir.A%40rockwellautomation.com&e=UJnpu3

## License

Proprietary - KnowledgeLens / Diageo
