# 🖋️ Writer

**Writer** is a Python-based service that stores sensor measurements into a PostgreSQL database. It provides an HTTP REST API to write and read sensor measurements, supporting various types of measurements, each represented as a time series.

🚧 **Status**: **Work in Progress**


## ✨ Features

- 📝 **Store sensor measurements**: Handles multiple types of sensor measurements, each represented as a time series.
- 📊 **Read sensor data**: Retrieve sensor data within specified time intervals.
- 🔄 **Dynamic Configuration**: Easily configure database connections and other settings via environment variables.

## 📦 Requirements

- 🐍 Python 3.12+
- 🐘 PostgreSQL
- 🐳 Docker & Docker Compose

## 🚀 Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Pa3kx/writer.git
   cd writer
   ...
