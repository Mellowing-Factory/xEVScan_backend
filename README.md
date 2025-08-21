# 🚗⚡ EV Scan API

**Electric Vehicle Diagnostic Scan Data Management API with Comprehensive Swagger Documentation**

[![Railway Deploy](https://img.shields.io/badge/Deploy%20on-Railway-purple)](https://railway.app/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)
[![Swagger](https://img.shields.io/badge/API-Swagger%20UI-orange.svg)](https://swagger.io/)

## 🎯 **Project Overview**

This API manages electric vehicle diagnostic scan data based on Korean EV standards, providing secure data ingestion from external scanners and real-time access for tablet applications with comprehensive health monitoring.

### **🏗️ Architecture**
- **Backend**: Flask with SQLAlchemy ORM
- **Database**: PostgreSQL with JSONB support
- **Authentication**: JWT-based with email verification
- **Documentation**: Interactive Swagger UI
- **Deployment**: Railway cloud platform
- **Security**: Input validation, CORS, environment variables

---

## 📋 **EV Scan Data Categories**

Based on Korean EV diagnostic specifications:

| Category | Korean | Parameters | Description |
|----------|--------|------------|-------------|
| **Battery** | 배터리 | 10 params | SoH, SoC, temperature, voltage deviation, cycles |
| **Motor** | 구동 모터 | 5 params | Torque, status checks, insulation, surge test |
| **Decelerator** | 감속기 | 4 params | Status, RPM, noise level, oil leak detection |
| **OBC** | 온보드차처 | 2 params | OBC status, BMS status monitoring |
| **EPCU** | 통합전력제어장치 | 3 params | Inverter, LDC, VCU status |

---

## 🚀 **Features**

### **🔐 Authentication & Security**
- Email-based user registration with verification
- JWT token authentication (7-day expiration)
- Password hashing with bcrypt
- Input validation and SQL injection protection
- CORS configuration for cross-origin requests

### **📊 Data Management**
- PostgreSQL database with JSONB flexibility
- Real-time EV scan data ingestion
- Batch processing for high-volume imports
- Device-user linking and access control
- Automatic health status calculation

### **📱 Tablet Application APIs**
- Authenticated data retrieval with pagination
- Device status monitoring and analytics
- Historical data filtering by date ranges
- Real-time health assessment dashboard
- Offline-capable data synchronization

### **🌐 External Integration**
- RESTful API for external scanner systems
- Flexible data schema supporting various EV models
- Bulk data import with error handling
- Real-time data validation and processing

### **📚 Interactive Documentation**
- Comprehensive Swagger UI at `/docs/`
- Try-it-out functionality for all endpoints
- Built-in authentication testing
- Request/response examples and validation
- Downloadable OpenAPI specification

---

## ⚡ **Quick Start**

### **Prerequisites**
- Python 3.8+
- PostgreSQL 13+
- Git

### **1. Clone Repository**
```bash
git clone <your-repository-url>
cd ev-scan-api
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Environment Setup**
```bash
cp .env.example .env
# Edit .env with your actual values
```

### **4. Generate Security Keys**
```bash
python -c "import secrets; print('SECRET_KEY:', secrets.token_hex(32)); print('JWT_SECRET_KEY:', secrets.token_hex(32))"
```

### **5. Initialize Database**
```bash
python database_setup.py
```

### **6. Run Application**
```bash
python app.py
```

### **7. Access Swagger Documentation**
Open: **http://localhost:5000/docs/**

---

## 🌐 **Deployment**

### **Railway Deployment (Recommended)**

1. **Push to GitHub**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Deploy to Railway**
   - Connect GitHub repository to Railway
   - Add PostgreSQL service
   - Set environment variables
   - Deploy automatically

3. **Configure Environment Variables**
   - `SECRET_KEY`: Your Flask secret key
   - `JWT_SECRET_KEY`: JWT signing key
   - `MAIL_USERNAME`: Email for verification
   - `MAIL_PASSWORD`: Email app password

4. **Initialize Production Database**
```bash
railway shell
python database_setup.py
```

**Detailed deployment guide**: [docs/deployment_guide.md](docs/deployment_guide.md)

---

## 📚 **API Documentation**

### **Interactive Documentation**
- **Swagger UI**: `/docs/` - Interactive API testing
- **Health Check**: `/` - System status endpoint
- **OpenAPI Spec**: `/docs/swagger.json` - API specification

### **Authentication Flow**
```bash
# 1. Register user
POST /api/auth/register

# 2. Login to get JWT token
POST /api/auth/login

# 3. Use token in Authorization header
Authorization: Bearer <your-jwt-token>
```

### **Key Endpoints**

#### **Authentication**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/verify/{token}` - Verify email address

#### **User & Device Management**
- `GET /api/user/profile` - Get user profile
- `GET /api/user/devices` - List linked devices
- `POST /api/user/devices` - Link new device
- `DELETE /api/user/devices/{device_id}` - Unlink device

#### **External Data Ingestion**
- `POST /api/external/scan-data` - Submit single scan
- `POST /api/external/scan-data/batch` - Bulk import scans

#### **Tablet Application**
- `GET /api/tablet/scan-data` - Get scan data with filters
- `GET /api/tablet/device-status` - Device status summary
- `GET /api/tablet/analytics/summary` - Analytics dashboard
- `GET /api/tablet/device/{device_id}/latest` - Latest device scan

#### **Data Specifications**
- `GET /api/data-spec` - Complete data specifications
- `GET /api/data-spec/validation-rules` - Validation rules

---

## 🏥 **Health Monitoring**

The API automatically calculates device health based on:

| Parameter | Acceptable Range | Health Impact |
|-----------|------------------|---------------|
| Battery SoH | ≥ 70% | Critical for battery life |
| Battery Temperature | 15°C - 45°C | Thermal management |
| Voltage Deviation | ≤ 0.04V | Cell balancing |
| Motor Torque | 950-1050 Nm | Performance indicator |
| Noise Level | < 100 dB | Mechanical health |
| Status Fields | "정상" | Overall system health |

**Health Levels**: `excellent` (90%+) → `good` (75%+) → `fair` (50%+) → `poor` (<50%)

---

## 🛠️ **Development**

### **Project Structure**
```
ev-scan-api/
├── app.py              # Main Flask application
├── config.py           # Configuration management
├── models.py           # Database models
├── swagger_models.py   # API documentation schemas
├── utils.py            # Utility functions
├── extensions.py       # Flask extensions
├── api/                # API endpoint modules
│   ├── auth_swagger.py       # Authentication endpoints
│   ├── user_swagger.py       # User management
│   ├── external_swagger.py   # External data ingestion
│   ├── tablet_swagger.py     # Tablet app endpoints
│   └── data_spec_swagger.py  # Data specifications
└── docs/               # Documentation
```

### **Adding New Features**

1. **Database Models**: Add to `models.py`
2. **API Endpoints**: Create new file in `api/`
3. **Swagger Models**: Add schemas to `swagger_models.py`
4. **Register Namespace**: Update `app.py`
5. **Tests**: Add tests for new functionality

### **Running Tests**
```bash
# Unit tests
python -m pytest tests/

# Coverage report
python -m pytest --cov=. tests/
```

---

## 🔒 **Security**

### **Security Features**
- ✅ JWT token authentication with expiration
- ✅ Password hashing with bcrypt
- ✅ Input validation and sanitization
- ✅ SQL injection protection via SQLAlchemy ORM
- ✅ CORS configuration for cross-origin requests
- ✅ Environment variable secret management
- ✅ Rate limiting ready (can be easily added)

### **Security Best Practices**
- Never commit `.env` files
- Use strong, randomly generated secret keys
- Regularly rotate JWT secrets
- Monitor for suspicious activity
- Keep dependencies updated

---

## 📈 **Monitoring & Performance**

### **Built-in Monitoring**
- Health check endpoint for uptime monitoring
- Railway platform metrics (CPU, memory, requests)
- Database performance monitoring
- Error logging and tracking

### **Performance Optimizations**
- Database indexing on frequently queried fields
- Pagination for large datasets
- Efficient bulk data processing
- Connection pooling for database access

---

## 🧪 **Testing**

### **API Testing with Swagger**
1. Open `/docs/` in your browser
2. Register a test user
3. Login to get JWT token
4. Click "Authorize" and enter token
5. Test all endpoints interactively

### **Sample Test Data**
```json
{
  "device_id": "TEST_EV_001",
  "battery": {
    "soh": 85.2,
    "soc": 67.8,
    "temperature": 28.5
  },
  "motor": {
    "torque_value": 1000.0,
    "status": "정상"
  }
}
```

---

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make changes and add tests
4. Commit changes: `git commit -m "Add new feature"`
5. Push to branch: `git push origin feature/new-feature`
6. Submit a pull request

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 **Support**

- **Documentation**: Check `/docs/` for interactive API docs
- **Issues**: Create GitHub issues for bugs or feature requests
- **Deployment**: See [deployment guide](docs/deployment_guide.md)
- **API Examples**: See [API examples](docs/api_examples.md)

---

## 🎯 **Roadmap**

- [ ] Real-time WebSocket connections for live data
- [ ] Advanced analytics and reporting features
- [ ] Multi-language support for Korean/English
- [ ] Mobile app SDK generation
- [ ] Machine learning health predictions
- [ ] Integration with popular EV diagnostic tools

---

**Built with ❤️ for the Electric Vehicle industry**

🚗⚡ **Happy Scanning!** ⚡🚗