# 🖋️ Writer

**Writer** is a Python-based service that stores sensor measurements into a PostgreSQL database. It provides an HTTP REST API to write and read sensor measurements, supporting various types of measurements, each represented as a time series.

🚧 **Status**: Almost Ready - Tests passing (Hours spent: ~20). I would like to perform Final polishing & checking in the afternoon/night (27.8). I spent the whole day trying to reconcile test session scope for db and function scope for app and gave up. and I am going to sleep at 2AM again.

## ✨ Features

- 📝 **Store sensor measurements**: Handles multiple types of sensor measurements, each represented as a time series.
- 📊 **Read sensor data**: Retrieve sensor data within specified time intervals.

## 📦 Requirements

- 🐍 Python 3.12+
- 🐘 PostgreSQL
- 🐳 Docker & Docker Compose
- 🛠️ [uv](https://astral.sh/blog/uv-unified-python-packaging)


## 🚀 Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Pa3kx/writer.git
   cd writer
   docker-compose up --build # Run prod
   docker-compose -f docker-compose.yml -f docker-compose.test.yml up --build # Run tests