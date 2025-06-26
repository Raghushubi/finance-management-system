# Personal Finance Management System

A comprehensive web-based personal finance management application built with **Flask** and **PostgreSQL**. This system allows users to track their financial transactions, manage assets and liabilities, monitor investments, set budgets, and generate financial reports.

---

## 🧑‍🤝‍🧑 Team Members

- Raghu Shubhangi
- Gutta Greeshmitha Sai
- Nandana Renjith
- Meenakshi 
- Akshaya R

---

## 📋 Project Overview

This Database Management System (DBMS) project provides a complete solution for personal financial management with the following key features:

- **User Authentication**: Secure login and registration system  
- **Transaction Management**: Track income and expense transactions  
- **Asset Management**: Monitor personal assets and their values  
- **Investment Tracking**: Track investment portfolios with profit/loss calculations  
- **Liability Management**: Keep track of debts and liabilities  
- **Budget Planning**: Set and monitor budgets across different categories  
- **Financial Reports**: Generate comprehensive financial reports  
- **User Profile Management**: Update personal information and preferences  

---

## 🛠️ Technology Stack

- **Backend**: Python Flask  
- **Database**: PostgreSQL  
- **Frontend**: HTML, CSS, JavaScript  
- **Database Connector**: psycopg2  

---

## 🗃️ Database Schema

The system uses a well-structured PostgreSQL database with the following tables:

- `users`: User authentication and profile information  
- `phone`: User phone numbers (supports multiple numbers)  
- `transaction_main`: Financial transactions  
- `transaction_type`: Transaction categories and types  
- `asset`: User assets and their values  
- `investment`: Investment portfolio tracking  
- `liability`: Debts and liabilities  
- `budget`: Budget planning and tracking  
- `credit_card`: Credit card information  

---

## ✅ Prerequisites

- Python
- PostgreSQL  
- pgAdmin 4 *(recommended for database management)*

---

## 🚀 Installation and Setup

### 1. Clone the Repository
```bash
git clone https://github.com/[your-username]/finance-management-system.git
cd finance-management-system
```

### 2. Install Python Dependencies
```bash
pip install flask psycopg2-binary
```

### 3. Database Setup

#### Step 3.1: Create the Database in pgAdmin 4
- Open **pgAdmin 4**
- Connect to your PostgreSQL server
- Right-click on **Databases** → **Create** → **Database...**
- Set the database name as: `financedatabs`
- Click **Save**

#### Step 3.2: Import Database Schema
- Right-click on the `financedatabs` database → **Query Tool**
- Open the `database_setup.sql` file from the project folder
- Copy its contents and paste into the Query Tool
- Execute the script (press F5 or the ▶️ Execute button)

✅ This will create all tables, constraints, and a test user.

---

### 4. Configure the Database Connection in `app.py`
```python
def get_db_connection():
    conn = psycopg2.connect(
        dbname="financedatabs",
        user="postgres",          # Update if your username is different
        password="postgres",      # Update if your password is different
        host="localhost",
        port="5432"
    )
    return conn
```

---

### 5. Run the Application
```bash
python app.py
```

The app will be available at:  
🔗 http://localhost:5000

---

## 🔐 Default Test User

Use the following credentials to log in:

- **Email**: `test@example.com`  
- **Password**: `test123`

---

## ✨ Features Overview

### 📊 Dashboard
- Overview of financial status
- Recent transactions
- Asset summary
- Investment portfolio
- Budget status

### 💰 Transaction Management
- Add income and expense transactions
- View transaction history
- Categorize transactions
- Real-time transaction processing

### 🏠 Asset Management
- Track personal assets
- Monitor asset values
- Purchase date tracking
- Asset categorization

### 📈 Investment Tracking
- Portfolio management
- Profit/loss calculations
- Current market value tracking
- Investment type categorization

### 🧾 Budget Planning
- Set budget limits by category
- Track budget utilization
- Budget period management
- Budget vs actual spending analysis

### 📑 Reports
- Weekly income/expense reports
- Financial summaries

---

## ⚙️ Development Notes

- Flask's built-in development server is used  
- Session-based login system via Flask session  
- Clean structure using:
  - `templates/` for HTML
  - `static/` for CSS & JS
- Error handlers implemented for 404 and 500 errors  
- Database queries optimized and committed safely  

---
