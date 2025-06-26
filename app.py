from flask import Flask, render_template, request, redirect, url_for, session, flash, g, jsonify
import psycopg2
from psycopg2 import sql
from datetime import datetime
from decimal import Decimal

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="financedatabs",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

@app.before_request
def load_user():
    g.user_id = session.get('user_id')
    g.username = session.get('username')

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
        else:
            email = request.form.get('email')
            password = request.form.get('password')
        
        conn = get_db_connection()
        if not conn:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Database connection error'}), 500
            flash('Database connection error.', 'error')
            return render_template('login.html')
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, username, password 
                FROM users 
                WHERE email = %s;
            """, (email,))
            user = cursor.fetchone()
            
            if user and user[2] == password:  
                session['user_id'] = user[0]
                session['username'] = user[1]
                if request.is_json:
                    return jsonify({
                        'success': True,
                        'message': 'Login successful'
                    })
                return redirect(url_for('dashboard'))
            else:
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid credentials'
                    }), 401
                flash('Invalid credentials.', 'error')
                
        except psycopg2.Error as e:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Database error occurred'}), 500
            flash('Database error occurred.', 'error')
            print(f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not g.user_id:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('login'))
    
    try:
        cursor = conn.cursor()
        
        # Fetch recent transactions
        cursor.execute("""
            SELECT tm.transaction_id, tm.transaction_amount, tt.transaction_type, 
                tt.transaction_category, tm.transaction_date
            FROM transaction_main tm
            JOIN transaction_type tt ON tm.transaction_type_id = tt.transaction_type_id
            WHERE tm.user_id = %s
            ORDER BY tm.transaction_date DESC
            LIMIT 5;
        """, (g.user_id,))
        transactions = cursor.fetchall()

        # Fetch assets
        cursor.execute("""
            SELECT asset_type, COALESCE(SUM(asset_value), 0) as total_value
            FROM asset
            WHERE user_id = %s
            GROUP BY asset_type;
        """, (g.user_id,))
        assets = cursor.fetchall()

        # Fetch investments
        cursor.execute("""
            SELECT investment_type, ticker, units, current_price, 
                   COALESCE(units * current_price, 0) as current_value
            FROM investment
            WHERE user_id = %s;
        """, (g.user_id,))
        investments = cursor.fetchall()

        # Fetch liabilities
        cursor.execute("""
            SELECT liability_type, COALESCE(SUM(liability_amount), 0) as total_amount
            FROM liability
            WHERE user_id = %s AND due_date >= CURRENT_DATE
            GROUP BY liability_type;
        """, (g.user_id,))
        liabilities = cursor.fetchall()

        # Fetch budget information
        cursor.execute("""
            SELECT budget_category, COALESCE(SUM(planned_amount), 0) as total_budget
            FROM budget
            WHERE user_id = %s AND budget_end_date >= CURRENT_DATE
            GROUP BY budget_category;
        """, (g.user_id,))
        budgets = cursor.fetchall()

        # Calculate total income
        cursor.execute("""
            SELECT COALESCE(SUM(tm.transaction_amount), 0)
            FROM transaction_main tm
            JOIN transaction_type tt ON tm.transaction_type_id = tt.transaction_type_id
            WHERE tt.transaction_type = 'Income' AND tm.user_id = %s;
        """, (g.user_id,))
        income = cursor.fetchone()[0]

        # Calculate total expenses
        cursor.execute("""
            SELECT COALESCE(SUM(tm.transaction_amount), 0)
            FROM transaction_main tm
            JOIN transaction_type tt ON tm.transaction_type_id = tt.transaction_type_id
            WHERE tt.transaction_type = 'Expense' AND tm.user_id = %s;
        """, (g.user_id,))
        expenses = cursor.fetchone()[0]

        return render_template('dashboard.html',
                            username=g.username,
                            transactions=transactions,
                            assets=assets,
                            investments=investments,
                            liabilities=liabilities,
                            budgets=budgets,
                            income=income,
                            expenses=expenses)

    except psycopg2.Error as e:
        flash('Error loading dashboard data.', 'error')
        print(f"Database error: {e}")
        return redirect(url_for('login'))
    finally:
        cursor.close()
        conn.close()

@app.route('/transactions')
def transactions():
    if not g.user_id:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('login'))
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tm.transaction_id, tm.transaction_amount, tt.transaction_type,
                   tt.transaction_category, tm.transaction_date
            FROM transaction_main tm
            JOIN transaction_type tt ON tm.transaction_type_id = tt.transaction_type_id
            WHERE tm.user_id = %s
            ORDER BY tm.transaction_date DESC;
        """, (g.user_id,))
        transactions = cursor.fetchall()
        
        return render_template('transaction.html', 
                             username=g.username,
                             transactions=transactions)
    except psycopg2.Error as e:
        flash('Error loading transactions.', 'error')
        print(f"Database error: {e}")
        return redirect(url_for('dashboard'))
    finally:
        cursor.close()
        conn.close()


@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': False, 'message': 'Invalid request method'}), 400
    
    if not g.user_id:
        return jsonify({'success': False, 'message': 'Please login to continue'}), 401
    
    try:
        data = request.get_json()
        
        required_fields = ['category', 'amount', 'date', 'type']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        try:
            amount = Decimal(str(data['amount']))
            if amount <= 0:
                raise ValueError
        except (ValueError, decimal.InvalidOperation):
            return jsonify({'success': False, 'message': 'Invalid amount'}), 400
        
        try:
            transaction_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid date format'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection error'}), 500
        
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT transaction_type_id 
                FROM transaction_type 
                WHERE transaction_category = %s AND transaction_type = %s;
            """, (data['category'], data['type']))
            
            type_result = cursor.fetchone()
            if not type_result:
                return jsonify({'success': False, 'message': 'Invalid transaction type/category'}), 400
            
            type_id = type_result[0]

            # Get next transaction ID
            cursor.execute("SELECT COALESCE(MAX(transaction_id), 0) + 1 FROM transaction_main")
            next_id = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO transaction_main 
                (transaction_id, transaction_amount, transaction_date, user_id, transaction_type_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING transaction_id;
            """, (next_id, amount, transaction_date, g.user_id, type_id))
            
            transaction_id = cursor.fetchone()[0]
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': 'Transaction added successfully',
                'transaction_id': transaction_id
            })
            
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Database error: {e}")
            return jsonify({'success': False, 'message': 'Error adding transaction'}), 500
        finally:
            cursor.close()
            
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        required = ['username', 'email', 'password']
        if not all(field in data for field in required):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get next user ID
        cursor.execute("SELECT COALESCE(MAX(user_id), 0) + 1 FROM users")
        user_id = cursor.fetchone()[0]

        # Insert user
        cursor.execute("""
            INSERT INTO users (user_id, username, email, password)
            VALUES (%s, %s, %s, %s)
            RETURNING user_id
        """, (user_id, data['username'], data['email'], data['password']))

        # Insert phone numbers if provided
        if 'phones' in data and data['phones']:
            cursor.execute("SELECT COALESCE(MAX(phone_id), 0) FROM phone")
            phone_id = (cursor.fetchone()[0] or 0) + 1
            
            for phone in data['phones']:
                cursor.execute("""
                    INSERT INTO phone (phone_id, user_id, phone_number)
                    VALUES (%s, %s, %s)
                """, (phone_id, user_id, phone))
                phone_id += 1

        conn.commit()
        return jsonify({'success': True, 'message': 'Registration successful'})

    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': 'Database error occurred'}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

@app.route('/investments')
def investments():
    if not g.user_id:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT investment_id, investment_type, ticker, units, purchase_price,
                   current_price, 
                   COALESCE(units * current_price, 0) as current_value,
                   COALESCE(units * current_price - units * purchase_price, 0) as profit_loss
            FROM investment
            WHERE user_id = %s;
        """, (g.user_id,))
        investments = cursor.fetchall()
        
        return render_template('investments.html', 
                             username=g.username,
                             investments=investments)
    except psycopg2.Error as e:
        flash('Error loading investments.', 'error')
        print(f"Database error: {e}")
        return redirect(url_for('dashboard'))
    finally:
        cursor.close()
        conn.close()

@app.route('/assets')
def assets():
    if not g.user_id:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT asset_id, asset_type, asset_value, purchase_date
            FROM asset
            WHERE user_id = %s
            ORDER BY asset_value DESC;
        """, (g.user_id,))
        assets = cursor.fetchall()
        
        return render_template('assets.html', 
                             username=g.username,
                             assets=assets)
    except psycopg2.Error as e:
        flash('Error loading assets.', 'error')
        print(f"Database error: {e}")
        return redirect(url_for('dashboard'))
    finally:
        cursor.close()
        conn.close()

@app.route('/add_asset', methods=['POST'])
def add_asset():
    if not g.user_id:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['assetType', 'assetValue', 'purchaseDate']):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection error'}), 500
        
        cursor = conn.cursor()
        
        try:
            # Get next asset ID - simple MAX + 1 approach
            cursor.execute("SELECT COALESCE(MAX(Asset_ID), 0) FROM Asset")
            next_asset_id = cursor.fetchone()[0] + 1
            
            # Insert the new asset
            cursor.execute("""
                INSERT INTO Asset (Asset_ID, User_ID, Asset_Type, Asset_Value, Purchase_Date)
                VALUES (%s, %s, %s, %s, %s)
            """, (next_asset_id, g.user_id, data['assetType'], data['assetValue'], data['purchaseDate']))
            
            conn.commit()
            return jsonify({'success': True, 'message': 'Asset added successfully'})
            
        except Exception as e:
            conn.rollback()
            print(f"Error adding asset: {e}")
            return jsonify({'success': False, 'message': 'Error adding asset'}), 500
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500
        
@app.route('/liabilities')
def liabilities():
    if not g.user_id:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT liability_id, liability_type, liability_amount,
                   interest_rate, due_date
            FROM liability
            WHERE user_id = %s
            ORDER BY due_date;
        """, (g.user_id,))
        liabilities = cursor.fetchall()
        
        return render_template('liabilities.html', 
                             username=g.username,
                             liabilities=liabilities)
    except psycopg2.Error as e:
        flash('Error loading liabilities.', 'error')
        print(f"Database error: {e}")
        return redirect(url_for('dashboard'))
    finally:
        cursor.close()
        conn.close()

@app.route('/budget')
def budget():
    if not g.user_id:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT budget_id, budget_category, planned_amount,
                   budget_start_date, budget_end_date
            FROM budget
            WHERE user_id = %s AND budget_end_date >= CURRENT_DATE
            ORDER BY budget_start_date;
        """, (g.user_id,))
        budgets = cursor.fetchall()
        
        return render_template('budget.html', 
                             username=g.username,
                             budgets=budgets)
    except psycopg2.Error as e:
        flash('Error loading budget data.', 'error')
        print(f"Database error: {e}")
        return redirect(url_for('dashboard'))
    finally:
        cursor.close()
        conn.close()

@app.route('/reports')
def reports():
    if not g.user_id:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        cursor = conn.cursor()
        
        # Get weekly income
        cursor.execute("""
            SELECT COALESCE(SUM(tm.transaction_amount), 0) AS total_income
            FROM transaction_main tm
            JOIN transaction_type tt ON tm.transaction_type_id = tt.transaction_type_id
            WHERE tm.user_id = %s AND tt.transaction_type = 'Income'
            AND tm.transaction_date >= CURRENT_DATE - INTERVAL '7 days';
        """, (g.user_id,))
        income = cursor.fetchone()[0]

        # Get weekly expenses
        cursor.execute("""
            SELECT COALESCE(SUM(tm.transaction_amount), 0) AS total_expenses
            FROM transaction_main tm
            JOIN transaction_type tt ON tm.transaction_type_id = tt.transaction_type_id
            WHERE tm.user_id = %s AND tt.transaction_type = 'Expense'
            AND tm.transaction_date >= CURRENT_DATE - INTERVAL '7 days';
        """, (g.user_id,))
        expenses = cursor.fetchone()[0]
        
        return render_template('reports.html', 
                             username=g.username,
                             income=income,
                             expenses=expenses)
    except psycopg2.Error as e:
        flash('Error loading report data.', 'error')
        print(f"Database error: {e}")
        return redirect(url_for('dashboard'))
    finally:
        cursor.close()
        conn.close()

@app.route('/profile')
def profile():
    if not g.user_id:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.username, u.email, p.phone_number
            FROM users u
            LEFT JOIN phone p ON u.user_id = p.user_id
            WHERE u.user_id = %s;
        """, (g.user_id,))
        user_data = cursor.fetchone()
        
        if user_data:
            return render_template('profile.html',
                                username=user_data[0],
                                email=user_data[1],
                                phone_number=user_data[2] if user_data[2] else 'Not Provided')
        else:
            flash('User data not found.', 'error')
            return redirect(url_for('dashboard'))
            
    except psycopg2.Error as e:
        flash('Error loading profile data.', 'error')
        print(f"Database error: {e}")
        return redirect(url_for('dashboard'))
    finally:
        cursor.close()
        conn.close()

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if not g.user_id:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'email' not in data:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        new_name = data['name'].strip()
        new_email = data['email'].strip()
        
        # Validate input
        if not new_name or not new_email:
            return jsonify({'success': False, 'message': 'Name and email cannot be empty'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection error'}), 500
        
        cursor = conn.cursor()
        
        # Check if email already exists for another user
        cursor.execute("""
            SELECT user_id FROM users 
            WHERE email = %s AND user_id != %s;
        """, (new_email, g.user_id))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'Email already in use'}), 400
        
        # Update user profile
        cursor.execute("""
            UPDATE users
            SET username = %s, email = %s
            WHERE user_id = %s
            RETURNING username;
        """, (new_name, new_email, g.user_id))
        
        updated_username = cursor.fetchone()[0]
        conn.commit()
        
        # Update session
        session['username'] = updated_username
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'username': updated_username
        })
        
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error: {e}")
        return jsonify({'success': False, 'message': 'Error updating profile'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Template filters
@app.template_filter('currency')
def currency_filter(value):
    if value is None:
        return "₹0.00"
    try:
        return f"₹{float(value):,.2f}"
    except (ValueError, TypeError):
        return "₹0.00"

@app.template_filter('date')
def date_filter(value):
    if not value:
        return ""
    try:
        if isinstance(value, str):
            value = datetime.strptime(value, '%Y-%m-%d')
        return value.strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        return ""

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)