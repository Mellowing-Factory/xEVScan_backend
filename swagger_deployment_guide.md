# Complete EV Scan API Deployment Guide with Swagger

## 📋 **Project Files Checklist**

Make sure you have all these files in your project:

```
ev-scan-api/
├── app.py                      ✅ Main app with Swagger
├── config.py                   ✅ Configuration
├── extensions.py               ✅ Flask extensions  
├── models.py                   ✅ Database models
├── utils.py                    ✅ Utility functions
├── swagger_models.py           ✅ Swagger schemas
├── requirements.txt            ✅ Dependencies (with Flask-RESTX)
├── railway.toml               ✅ Railway config
├── .env.example               ✅ Environment template
├── database_setup.py          ✅ DB initialization
│
└── api/                       
    ├── __init__.py            ⚠️  CREATE THIS (empty file)
    ├── auth_swagger.py        ✅ Auth API with Swagger
    ├── user_swagger.py        ✅ User API with Swagger  
    ├── external_swagger.py    ✅ External API with Swagger
    ├── tablet_swagger.py      ✅ Tablet API with Swagger
    └── data_spec_swagger.py   ✅ Data Spec API with Swagger
```

## 🚀 **Step-by-Step Deployment**

### **Step 1: Create Missing Files**

Create an empty file at `api/__init__.py`:
```python
# This file makes 'api' a Python package
# Leave this file empty
```

### **Step 2: Set Up GitHub Repository**

1. **Create new GitHub repository**
2. **Upload all project files** to the repository
3. **Commit and push** to main branch

```bash
git init
git add .
git commit -m "Initial EV Scan API with Swagger documentation"
git branch -M main
git remote add origin https://github.com/yourusername/ev-scan-api.git
git push -u origin main
```

### **Step 3: Deploy to Railway**

#### **Option A: Deploy from GitHub (Recommended)**
1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your **ev-scan-api** repository
5. Railway will automatically detect Python and start building

#### **Option B: Deploy using Railway CLI**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project in your directory
railway init

# Deploy
railway up
```

### **Step 4: Add PostgreSQL Database**

1. In your Railway project dashboard, click **"New Service"**
2. Select **"Database"** > **"PostgreSQL"**
3. Railway will automatically create and link the database
4. The `DATABASE_URL` environment variable will be set automatically

### **Step 5: Configure Environment Variables**

In Railway project dashboard, go to **"Variables"** and add:

```bash
# Security Keys (GENERATE NEW ONES!)
SECRET_KEY=your_32_character_secret_key_here
JWT_SECRET_KEY=your_32_character_jwt_secret_key_here

# Email Configuration (for verification emails)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_gmail_app_password
```

#### **Generate Secret Keys:**
```bash
python3 -c "import secrets; print('SECRET_KEY:', secrets.token_hex(32)); print('JWT_SECRET_KEY:', secrets.token_hex(32))"
```

#### **Gmail App Password Setup:**
1. Enable 2-factor authentication on Gmail
2. Go to Google Account settings > Security > App passwords
3. Generate app password for "Mail"
4. Use this password in `MAIL_PASSWORD`

### **Step 6: Initialize Database**

After deployment, initialize the database tables:

#### **Option A: Using Railway CLI**
```bash
# Connect to your Railway environment
railway shell

# Run database setup
python database_setup.py
```

#### **Option B: One-time script**
Add this temporarily to the end of your `app.py`:
```python
# Add temporarily for first deployment only
@app.before_first_request
def create_tables():
    db.create_all()
```

### **Step 7: Test Your Deployment**

1. **Get your Railway URL** (e.g., `https://your-app.railway.app`)

2. **Test health check:**
```bash
curl https://your-app.railway.app/
```

3. **Access Swagger Documentation:**
   - Open: `https://your-app.railway.app/docs/`
   - You should see the interactive API documentation!

## 🎯 **Testing Your APIs with Swagger**

### **Access Swagger UI**
- **URL**: `https://your-app.railway.app/docs/`
- **Features**: Interactive testing, authentication, examples

### **Step-by-Step API Testing:**

#### **1. Test User Registration**
1. Open Swagger UI at `/docs/`
2. Navigate to **"auth"** > **"POST /api/auth/register"**
3. Click **"Try it out"**
4. Use this example data:
```json
{
  "email": "test@example.com",
  "password": "password123",
  "name": "Test User"
}
```
5. Click **"Execute"**
6. Should return `201 Created` with success message

#### **2. Test User Login**
1. Go to **"auth"** > **"POST /api/auth/login"**
2. Click **"Try it out"**
3. Use the same email/password from registration
4. Click **"Execute"**
5. Copy the `access_token` from the response

#### **3. Authenticate in Swagger**
1. Click the **🔒 "Authorize"** button at the top of Swagger UI
2. Enter: `Bearer YOUR_ACCESS_TOKEN_HERE`
3. Click **"Authorize"**
4. Now all authenticated endpoints will work!

#### **4. Test Device Management**
1. Go to **"user"** > **"POST /api/user/devices"**
2. Click **"Try it out"**
3. Add a test device:
```json
{
  "device_id": "TEST_DEVICE_001",
  "device_name": "Test EV Scanner"
}
```

#### **5. Test External Data Ingestion**
1. Go to **"external"** > **"POST /api/external/scan-data"**
2. Click **"Try it out"**
3. Submit test scan data:
```json
{
  "device_id": "TEST_DEVICE_001",
  "scan_timestamp": "2025-08-21T10:30:00",
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

#### **6. Test Tablet API**
1. Go to **"tablet"** > **"GET /api/tablet/scan-data"**
2. Click **"Try it out"**
3. Click **"Execute"**
4. Should return the scan data you just submitted!

## 🔧 **Advanced Configuration**

### **Custom Domain Setup**
1. In Railway dashboard: **"Settings"** > **"Domains"**
2. Add your custom domain
3. Configure DNS as instructed by Railway

### **Environment-Specific Configs**
```python
# In config.py, add different environments:
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
```

### **Monitoring Setup**
```python
# Add to app.py for production monitoring
import logging

if not app.debug:
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    app.logger.info('EV Scan API startup')
```

## 📊 **Swagger Features Guide**

### **API Documentation Features:**
- ✅ **Interactive Testing**: Test APIs directly in browser
- ✅ **Authentication**: Built-in JWT token management  
- ✅ **Request Examples**: Pre-filled example data
- ✅ **Response Schemas**: See exactly what data is returned
- ✅ **Error Documentation**: All error codes and messages
- ✅ **Download Spec**: Export OpenAPI specification

### **Developer Tools:**
- ✅ **Copy as cURL**: Generate cURL commands automatically
- ✅ **Multiple Formats**: JSON, form-data, etc.
- ✅ **Real-time Validation**: Immediate feedback on requests
- ✅ **Schema Browsing**: Explore data models

## 🎉 **Production Checklist**

### **Security ✅**
- [ ] Environment variables for all secrets
- [ ] HTTPS enabled (Railway handles this)
- [ ] Strong JWT secret keys
- [ ] Input validation on all endpoints
- [ ] CORS properly configured

### **Performance ✅**  
- [ ] Database indexes added
- [ ] Query optimization
- [ ] Pagination implemented
- [ ] Error handling with rollbacks

### **Monitoring ✅**
- [ ] Health check endpoint working
- [ ] Railway metrics enabled
- [ ] Database connection monitoring
- [ ] Error logging configured

### **Documentation ✅**
- [ ] Swagger UI accessible
- [ ] All endpoints documented
- [ ] Example requests/responses
- [ ] Authentication instructions

## 🚨 **Troubleshooting**

### **Common Issues:**

#### **Swagger UI Not Loading**
- Check if Flask-RESTX is installed: `pip install Flask-RESTX==1.3.0`
- Verify all namespace imports in `app.py`
- Check Railway logs for import errors

#### **Database Connection Errors**
- Verify PostgreSQL service is running in Railway
- Check `DATABASE_URL` environment variable
- Run `database_setup.py` to create tables

#### **Authentication Errors in Swagger**
- Make sure JWT_SECRET_KEY is set
- Verify token format: `Bearer YOUR_TOKEN`
- Check token expiration (7 days default)

#### **Import Errors**
- Ensure `api/__init__.py` exists (even if empty)
- Check all file names match exactly
- Verify Python path in Railway

### **Getting Help:**
- **Railway Logs**: Check deployment logs in Railway dashboard
- **Local Testing**: Run `python app.py` locally first
- **Database Status**: Use Railway database connection tool
- **Environment Variables**: Double-check all required variables are set

## 🎯 **Next Steps**

Once deployed successfully:

1. **Share Swagger URL** with your team: `https://your-app.railway.app/docs/`
2. **Test all endpoints** using the interactive documentation
3. **Integrate with tablet app** using the provided client examples
4. **Set up external data sources** to send data to your API
5. **Monitor performance** using Railway's built-in metrics

Your EV Scan API with comprehensive Swagger documentation is now ready for production use! 🚀