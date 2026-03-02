# 📈 MonitoringFromIB 
### High-Performance Asynchronous Price Tracking System built with FastAPI

This project is a powerful tool designed to automate the collection and analysis of price data. It efficiently tracks product price dynamics using Python's asynchronous capabilities to handle multiple requests and parsing tasks concurrently.

---

## 🔗 Live Environment
- **Interactive API Documentation (Swagger UI):** [https://monitoringfromib-api.onrender.com/docs](https://monitoringfromib-api.onrender.com/docs)
- **Deployment Platform:** Render Cloud
- **Database:** Managed PostgreSQL Service

## 🛠 Tech Stack
* **Framework:** Python 3.11, FastAPI
* **Database & ORM:** PostgreSQL, SQLAlchemy (Async), Alembic (Migrations)
* **Authentication:** JWT (Access/Refresh tokens), Passlib (bcrypt)
* **Operations:** Docker, Docker Compose, Render
* **Data Collection:** aiohttp, BeautifulSoup4 (Fully Asynchronous)

## 🌟 Key Features
1. **Asynchronous Scraping:** The parser runs in concurrent mode, ensuring the API remains responsive during data collection cycles.
2. **Secure Architecture:** Modern JWT-based authentication for user registration, login, and protected routes.
3. **Containerization:** Fully Dockerized environment for consistent deployment across local and production servers.
4. **Structured Logging:** Comprehensive system events logging—from database operations to parsing results.
5. **RESTful API:** Clean and well-documented endpoints following industry standards.
6. **Background Task Execution:** Long-running scraping processes are delegated to FastAPI `BackgroundTasks`, keeping the API instantly responsive for clients.
7. **Smart Rate Limiting & RBAC:** A custom, database-backed rate limiter prevents server overload by enforcing a 1-hour cooldown for standard users, seamlessly integrated with Role-Based Access Control for administrative overrides.

## 📥 Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/IsmailBinnatov/monitoringfromib.git
   cd monitoringfromib
   ```
2. **Configure Environment:**
   Create a `.env` file in the root directory and specify your PostgreSQL credentials.
3. **Launch with Docker:**
   ```bash
   docker-compose up -d --build
   ```
4. **Apply Database Schema:**
   ```bash
   alembic upgrade head
   ```

---
**Developed by:** Ismail Binnatov | [GitHub Profile](https://github.com/IsmailBinnatov)