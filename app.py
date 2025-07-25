from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import datetime
from datetime import datetime, timedelta
from flask_mail import Mail, Message
app = Flask(__name__)
app.secret_key = 'moji-secret-key'



app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='lmoksha.132@gmail.com',
    MAIL_PASSWORD='mpul kfev dcju ucji'
)
mail = Mail(app)

@app.route('/send_reminders')
def send_reminders():
    conn = get_db_connection()
    target_date = (datetime.today() + timedelta(days=3)).date()
    reminders = conn.execute('''
        SELECT u.email, u.name, br.title, br.due_date
        FROM book_requests br
        JOIN users u ON br.user_id = u.id
        WHERE br.status = 'Approved' AND due_date = ?
    ''', (target_date,)).fetchall()
    conn.close()

    for r in reminders:
        msg = Message(
            subject="Library Book Due Reminder",
            sender="your_email@gmail.com",
            recipients=[r['email']],
            body=f"Hi {r['name']},\n\nYour book '{r['title']}' is due on {r['due_date']}. Please return it on time to avoid a fine."
        )
        mail.send(msg)

    return "Reminders sent"

# Initialize SQLite database connection
def get_db_connection():
    conn = sqlite3.connect('lms.db')
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn = get_db_connection()

    # Create book_requests table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS book_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            request_date DATE DEFAULT CURRENT_DATE
        );
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL
        );
    ''')
    # Create books table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            pages INTEGER NOT NULL,
            price REAL NOT NULL
        );
    ''')

    # Create issues table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            issue_date DATE NOT NULL,
            return_date DATE,
            FOREIGN KEY(book_id) REFERENCES books(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    ''')

    conn.commit()
    conn.close()

    
    
def create_issued_books_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS issued_books (
            issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            book_id INTEGER,
            issue_date TEXT,
            due_date TEXT,
            return_date TEXT,
            fine REAL DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(book_id) REFERENCES books(id)
        )
    ''')
    conn.commit()
    conn.close()

# Seed sample books (only if empty)
def seed_sample_books():
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) FROM books').fetchone()[0]
    if count == 0:
        sample_books = [
            ('To Kill a Mockingbird', 'Harper Lee', 281, 9.99),
            ('1984', 'George Orwell', 328, 8.99),
            ('Pride and Prejudice', 'Jane Austen', 279, 7.99),
            ('The Great Gatsby', 'F. Scott Fitzgerald', 180, 10.50),
            ('Moby Dick', 'Herman Melville', 635, 12.00),
            ('War and Peace', 'Leo Tolstoy', 1225, 14.99),
            ('The Catcher in the Rye', 'J.D. Salinger', 214, 8.50),
            ('Crime and Punishment', 'Fyodor Dostoevsky', 430, 11.20),
            ('The Hobbit', 'J.R.R. Tolkien', 310, 9.30),
            ('Brave New World', 'Aldous Huxley', 268, 8.75),
            ('Jane Eyre', 'Charlotte Brontë', 500, 9.40),
            ('The Odyssey', 'Homer', 541, 10.00),
            ('The Divine Comedy', 'Dante Alighieri', 798, 11.50),
            ('The Brothers Karamazov', 'Fyodor Dostoevsky', 824, 12.75),
            ('Wuthering Heights', 'Emily Brontë', 416, 8.90),
            ("Harry Potter and the Sorcerer's Stone", 'J.K. Rowling', 309, 14.99),
            ('The Lord of the Rings', 'J.R.R. Tolkien', 1178, 20.00),
            ('The Alchemist', 'Paulo Coelho', 197, 7.99),
            ('Les Misérables', 'Victor Hugo', 1463, 13.25),
            ('The Chronicles of Narnia', 'C.S. Lewis', 767, 15.00),
            ('The Catch-22', 'Joseph Heller', 453, 12.99),
            ('Beloved', 'Toni Morrison', 324, 14.50),
            ('The Kite Runner', 'Khaled Hosseini', 371, 13.75),
            ('The Road', 'Cormac McCarthy', 287, 15.00),
            ('Fahrenheit 451', 'Ray Bradbury', 194, 11.20),
            ('A Tale of Two Cities', 'Charles Dickens', 489, 10.99),
            ('Don Quixote', 'Miguel de Cervantes', 863, 16.50),
            ('The Count of Monte Cristo', 'Alexandre Dumas', 1276, 18.75),
            ('Dracula', 'Bram Stoker', 418, 9.95),
            ('Frankenstein', 'Mary Shelley', 280, 8.50),
            ('Anna Karenina', 'Leo Tolstoy', 864, 15.99),
            ('The Picture of Dorian Gray', 'Oscar Wilde', 254, 7.99),
            ('The Grapes of Wrath', 'John Steinbeck', 464, 14.00),
            ('Lolita', 'Vladimir Nabokov', 336, 13.50),
            ('Catch-22', 'Joseph Heller', 453, 12.99),
            ('Great Expectations', 'Charles Dickens', 505, 11.25),
            ('The Secret Garden', 'Frances Hodgson Burnett', 331, 9.50),
            ('The Jungle', 'Upton Sinclair', 390, 12.75),
            ('Slaughterhouse-Five', 'Kurt Vonnegut', 215, 10.00),
            ('Invisible Man', 'Ralph Ellison', 581, 13.99),
            ('The Bell Jar', 'Sylvia Plath', 244, 11.99),
            ('One Hundred Years of Solitude', 'Gabriel Garcia Marquez', 417, 14.50),
            ('The Sound and the Fury', 'William Faulkner', 326, 12.99),
            ('Gone with the Wind', 'Margaret Mitchell', 1037, 19.99),
            ('Rebecca', 'Daphne du Maurier', 449, 11.50),
            ('The Old Man and the Sea', 'Ernest Hemingway', 127, 7.50),
            ('The Handmaid’s Tale', 'Margaret Atwood', 311, 14.25),
            ('The Sun Also Rises', 'Ernest Hemingway', 251, 10.50),
            ('A Clockwork Orange', 'Anthony Burgess', 192, 8.95),
            ('The Stranger', 'Albert Camus', 123, 9.99),
            ('The Metamorphosis', 'Franz Kafka', 201, 7.25),
            ('Heart of Darkness', 'Joseph Conrad', 152, 9.00),
            ('The Iliad', 'Homer', 683, 16.00),
            ('The Canterbury Tales', 'Geoffrey Chaucer', 528, 18.50),
            ('Les Fleurs du mal', 'Charles Baudelaire', 150, 11.99),
            ('The Trial', 'Franz Kafka', 255, 10.75),
            ('East of Eden', 'John Steinbeck', 601, 15.99),
            ('A Farewell to Arms', 'Ernest Hemingway', 355, 12.00),
            ('The Scarlet Letter', 'Nathaniel Hawthorne', 272, 10.00),
            ('David Copperfield', 'Charles Dickens', 624, 14.25),
            ('The Adventures of Huckleberry Finn', 'Mark Twain', 366, 11.50),
            ('The Odyssey', 'Homer', 541, 15.00),
            ('Middlemarch', 'George Eliot', 800, 18.75),
            ('The Call of the Wild', 'Jack London', 232, 9.99),
            ('The Poisonwood Bible', 'Barbara Kingsolver', 546, 14.99),
            ('Gulliver’s Travels', 'Jonathan Swift', 306, 9.50),
            ('The Count of Monte Cristo', 'Alexandre Dumas', 1276, 18.75),
            ('The Brothers Karamazov', 'Fyodor Dostoevsky', 824, 16.50),
            ('Crime and Punishment', 'Fyodor Dostoevsky', 671, 14.25),
            ('Les Miserables', 'Victor Hugo', 1232, 20.00),
            ('War and Peace', 'Leo Tolstoy', 1225, 19.50),
            ('Anna Karenina', 'Leo Tolstoy', 864, 15.99),
            ('Don Quixote', 'Miguel de Cervantes', 863, 16.50),
            ('The Divine Comedy', 'Dante Alighieri', 798, 17.00),
            ('Moby-Dick', 'Herman Melville', 720, 13.99),
            ('The Hobbit', 'J.R.R. Tolkien', 310, 12.99),
            ('The Lord of the Rings', 'J.R.R. Tolkien', 1178, 25.00),
            ('Harry Potter and the Chamber of Secrets', 'J.K. Rowling', 341, 14.50),
            ('Harry Potter and the Prisoner of Azkaban', 'J.K. Rowling', 435, 15.00),
            ('Harry Potter and the Goblet of Fire', 'J.K. Rowling', 636, 17.50),
            ('Harry Potter and the Order of the Phoenix', 'J.K. Rowling', 766, 18.00),
            ('Harry Potter and the Half-Blood Prince', 'J.K. Rowling', 607, 16.50),
            ('Harry Potter and the Deathly Hallows', 'J.K. Rowling', 759, 20.00),
            ('The Hunger Games', 'Suzanne Collins', 374, 14.99),
            ('Catching Fire', 'Suzanne Collins', 391, 15.50),
            ('Mockingjay', 'Suzanne Collins', 390, 15.75),
            ('Dune', 'Frank Herbert', 412, 13.50),
            ('Ender’s Game', 'Orson Scott Card', 324, 12.00),
            ('The Martian', 'Andy Weir', 369, 14.99),
            ('Ready Player One', 'Ernest Cline', 374, 14.00),
            ('The Fault in Our Stars', 'John Green', 313, 11.50),
        ]
        

        conn.executemany(
            'INSERT INTO books (title, author, pages, price) VALUES (?, ?, ?, ?)',
            sample_books
        )
        
        conn.commit()
    conn.close()

# Home route
@app.route('/')
def home():
    return render_template("base.html")

# -------------------- USER REGISTRATION --------------------
@app.route('/register/user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()
        password = request.form['password'].strip()

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO users (username, email, phone, password) VALUES (?, ?, ?, ?)",
                (username, email, phone, password)
            )
            conn.commit()
            flash('User registered successfully!', 'success')
            return redirect(url_for('home'))
        except sqlite3.IntegrityError:
            flash('Username or Email already exists.', 'danger')
        finally:
            conn.close()

    return render_template('register_user.html')


# -------------------- ADMIN LOGIN --------------------
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'moksha' and password == 'moksha132':
            session['admin'] = username
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'danger')
            return redirect(url_for('admin_login'))
    
    return render_template('base.html')
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

# -------------------- ADMIN DASHBOARD --------------------
@app.route('/admin/dashboard', endpoint='admin_dashboard')

def admin_dashboard():
    if 'admin' not in session:
        flash('Please log in as admin to access the dashboard.', 'warning')
        return redirect(url_for('admin_login'))

    query = request.args.get('query', '').strip()
    conn = get_db_connection()

    if query:
        sql = "SELECT * FROM books WHERE title LIKE ? OR author LIKE ?"
        like_query = f"%{query}%"
        books = conn.execute(sql, (like_query, like_query)).fetchall()
    else:
        books = conn.execute('SELECT * FROM books').fetchall()

    conn.close()
    return render_template('admin_dashboard.html', books=books)

# ------------------ USER LOGIN ------------------
@app.route('/login_user', methods=['POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
    conn.close()

    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        flash('Login successful!', 'success')
        return redirect(url_for('user_dashboard'))
    else:
        flash('Invalid username or password.', 'danger')
        return redirect(url_for('home'))



# ------------------ USER DASHBOARD ------------------
@app.route('/user/dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('login'))

    conn = get_db_connection()
    books = conn.execute("SELECT * FROM books").fetchall()

    issued_books = conn.execute("""SELECT ib.issue_id, b.title, ib.issue_date, ib.due_date, ib.return_date, ib.fine
 
        FROM issued_books ib 
        JOIN books b ON ib.book_id = b.id 
        WHERE ib.user_id = ?
        ORDER BY ib.issue_date DESC
    """, (session['user_id'],)).fetchall()
    conn.close()

    return render_template("user_dashboard.html", books=books, issued_books=issued_books)





# -------------------- BOOKS MANAGEMENT --------------------



@app.route('/books/add', methods=['POST'])
def add_book():
    if 'admin' not in session:
        flash('Access denied.', 'danger')
        return redirect(url_for('admin_login'))

    title = request.form['title'].strip()
    author = request.form['author'].strip()
    pages = request.form['pages'].strip()
    price = request.form['price'].strip()

    if not title or not author:
        flash('Title and Author are required.', 'warning')
        return redirect(url_for('books'))

    try:
        pages = int(pages)
    except ValueError:
        pages = 0

    try:
        price = float(price)
    except ValueError:
        price = 0.0

    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO books (title, author, pages, price) VALUES (?, ?, ?, ?)',
            (title, author, pages, price)
        )
        conn.commit()
        flash('Book added successfully!', 'success')
    except sqlite3.Error as e:
        flash(f'Error adding book: {str(e)}', 'danger')
    finally:
        conn.close()

    return redirect(url_for('user_dashboard'))


@app.route('/books/edit/<int:book_id>', methods=['POST'])
def edit_book(book_id):
    if 'admin' not in session:
        flash('Access denied.', 'danger')
        return redirect(url_for('admin_login'))

    title = request.form['title'].strip()
    author = request.form['author'].strip()
    pages = request.form['pages'].strip()
    price = request.form['price'].strip()

    try:
        pages = int(pages)
    except ValueError:
        pages = 0
    try:
        price = float(price)
    except ValueError:
        price = 0.0

    try:
        conn = get_db_connection()
        conn.execute('''
            UPDATE books SET title = ?, author = ?, pages = ?, price = ?
            WHERE id = ?
        ''', (title, author, pages, price, book_id))
        conn.commit()
        flash('Book updated successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Error updating book.', 'danger')
    finally:
        conn.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/books/delete/<int:book_id>')
def delete_book(book_id):
    if 'admin' not in session:
        flash('Access denied.', 'danger')
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))



# -------------------- MEMBERS MANAGEMENT --------------------
@app.route('/members')
def members():
    if 'admin' not in session:
        flash('Access denied. Please login as admin.', 'danger')
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    members = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('members.html', members=members)
# Add Member
@app.route('/members/add', methods=['POST'])
def add_member():
    if 'admin' not in session:
        flash('Access denied.', 'danger')
        return redirect(url_for('admin_login'))

    username = request.form['username'].strip()
    email = request.form['email'].strip()
    phone = request.form['phone'].strip()

    try:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO users (username, email, phone, password) VALUES (?, ?, ?, ?)",
            (username, email, phone, 'defaultpassword')  # or generate random / let user set password separately
        )
        conn.commit()
        flash('Member added successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Username or Email already exists.', 'danger')
    finally:
        conn.close()

    return redirect(url_for('members'))

# Edit Member
@app.route('/members/edit/<int:member_id>', methods=['POST'])
def edit_member(member_id):
    if 'admin' not in session:
        flash('Access denied.', 'danger')
        return redirect(url_for('admin_login'))

    username = request.form['username'].strip()
    email = request.form['email'].strip()
    phone = request.form['phone'].strip()

    try:
        conn = get_db_connection()
        conn.execute('''
            UPDATE users SET username = ?, email = ?, phone = ?
            WHERE id = ?
        ''', (username, email, phone, member_id))
        conn.commit()
        flash('Member updated successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Username or Email already exists.', 'danger')
    finally:
        conn.close()

    return redirect(url_for('members'))

# Delete Member
@app.route('/members/delete/<int:member_id>')
def delete_member(member_id):
    if 'admin' not in session:
        flash('Access denied.', 'danger')
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (member_id,))
    conn.commit()
    conn.close()
    flash('Member deleted successfully!', 'success')
    return redirect(url_for('members'))


@app.route('/user/return/<int:request_id>', methods=['POST'])
def return_books(request_id):
    conn = get_db_connection()
    request_data = conn.execute('SELECT due_date FROM book_requests WHERE id = ?', (request_id,)).fetchone()

    today = datetime.today().date()
    due_date = datetime.strptime(request_data['due_date'], "%Y-%m-%d").date()

    fine = 0
    if today > due_date:
        days_late = (today - due_date).days
        fine = days_late * 5  # ₹5/day fine

    conn.execute('UPDATE book_requests SET status = "Returned", fine = ? WHERE id = ?', (fine, request_id))
    conn.commit()
    conn.close()

    flash(f"Book returned. Fine: ₹{fine}", "info")
    return redirect(url_for('user_dashboard'))

# -------------------- REPORTS --------------------

@app.route('/reports')
def reports():
    if 'admin' not in session:
        flash('Access denied. Please login as admin.', 'danger')
        return redirect(url_for('admin_login'))

    conn = get_db_connection()

    today = datetime.today()
    one_week_ago = today - timedelta(days=7)
    one_month_ago = today - timedelta(days=30)
    one_year_ago = today - timedelta(days=365)

    # Total books issued in last week, month, year
    weekly_issued = conn.execute(
        'SELECT COUNT(*) FROM issues WHERE issue_date BETWEEN ? AND ?',
        (one_week_ago.date(), today.date())
    ).fetchone()[0]

    monthly_issued = conn.execute(
        'SELECT COUNT(*) FROM issues WHERE issue_date BETWEEN ? AND ?',
        (one_month_ago.date(), today.date())
    ).fetchone()[0]

    yearly_issued = conn.execute(
        'SELECT COUNT(*) FROM issues WHERE issue_date BETWEEN ? AND ?',
        (one_year_ago.date(), today.date())
    ).fetchone()[0]

    # Total members
    total_members = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]

    # Total books in library
    total_books = conn.execute('SELECT COUNT(*) FROM books').fetchone()[0]

    conn.close()

    return render_template(
        'reports.html',
        weekly_issued=weekly_issued,
        monthly_issued=monthly_issued,
        yearly_issued=yearly_issued,
        total_members=total_members,
        total_books=total_books
    )
# Show books available to issue
@app.route('/user/issue')
def user_issue():
    if 'user_email' not in session:
        return redirect(url_for('user_login'))
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books WHERE copies > 0').fetchall()
    conn.close()
    return render_template('user_issue.html', books=books)

# Issue a book
@app.route('/issue/<int:book_id>', methods=['POST'])
def issue_book(book_id):
    if 'user_id' not in session:
        flash("Please login to issue a book", "warning")
        return redirect(url_for('user_login'))

    user_id = session['user_id']
    today = datetime.today()
    due_date = today + timedelta(days=7)

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO issued_books (user_id, book_id, issue_date, due_date)
        VALUES (?, ?, ?, ?)
    ''', (user_id, book_id, today, due_date))
    conn.commit()
    conn.close()

    flash("Book issued successfully! Please return within 7 days.", "success")
    return redirect(url_for('my_books'))  # or dashboard
# Return a book
from datetime import datetime

@app.route('/return/<int:issue_id>', methods=['POST'])
def return_book(issue_id):
    conn = get_db_connection()

    # Make sure the column is 'issue_id', not 'id'
    issue = conn.execute("SELECT * FROM issued_books WHERE issue_id = ?", (issue_id,)).fetchone()

    if issue is None:
        flash("Issued book not found.", "danger")
        conn.close()
        return redirect(url_for('user_dashboard'))

    # Check if already returned
    if issue['return_date']:
        flash("Book already returned.", "warning")
        conn.close()
        return redirect(url_for('user_dashboard'))

    from datetime import datetime

    return_date = datetime.now().strftime("%Y-%m-%d")
    due_date = datetime.strptime(issue['due_date'], "%Y-%m-%d")
    returned_date = datetime.strptime(return_date, "%Y-%m-%d")

    days_late = (returned_date - due_date).days
    fine = max(0, days_late * 10)  # ₹10 per day late

    # Update issued_books with return_date and fine
    conn.execute("""
        UPDATE issued_books
        SET return_date = ?, fine = ?
        WHERE issue_id = ?
    """, (return_date, fine, issue_id))

    
    flash("Book returned successfully!", "success")
    return redirect(url_for('user_dashboard'))


@app.route('/user/request_book')
def request_book_form():
    if 'user_id' not in session:
        flash('Please log in to request books.')
        return redirect(url_for('login'))
    return render_template('request_book.html')

@app.route('/user/request_book', methods=['POST'])
def submit_book_request():
    if 'user_id' not in session:
        flash('Please log in to request books.')
        return redirect(url_for('login'))

    title = request.form['title']
    author = request.form['author']
    user_id = session['user_id']

    conn = get_db_connection()
    conn.execute('INSERT INTO book_requests (user_id, title, author) VALUES (?, ?, ?)',
                 (user_id, title, author))
    conn.commit()
    conn.close()

    flash('Your book request has been submitted.')
    return redirect(url_for('user_dashboard'))
@app.route('/user/request_book/<int:book_id>', methods=['POST'])
def request_book(book_id):
    if 'user_id' not in session:
        flash("Login first", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    
    if not book:
        flash("Book not found", "danger")
        return redirect(url_for('user_dashboard'))

    # Check if already requested
    existing = conn.execute('SELECT * FROM book_requests WHERE user_id = ? AND book_id = ? AND status = "pending"', (session['user_id'], book_id)).fetchone()
    if existing:
        flash("You have already requested this book", "warning")
        conn.close()
        return redirect(url_for('user_dashboard'))

    conn.execute('''
        INSERT INTO book_requests (user_id, book_id, book_title, book_author, status)
        VALUES (?, ?, ?, ?, 'pending')
    ''', (session['user_id'], book_id, book['title'], book['author']))
    conn.commit()
    conn.close()

    flash("Book request sent to admin!", "success")
    return redirect(url_for('user_dashboard'))

# View issued books and fine status
@app.route('/user/my_books')
def my_books():
    if 'user_email' not in session:
        return redirect(url_for('login_user'))

    conn = get_db_connection()
    books = conn.execute('''
        SELECT issues.*, books.title, books.author
        FROM issues
        JOIN books ON issues.book_id = books.id
        WHERE issues.user_email = ?
        ORDER BY issues.issue_date DESC
    ''', (session['user_email'],)).fetchall()
    conn.close()
    return render_template('my_books.html', books=books)
@app.route('/user/issue_books')
def issue_books_page():
    if 'user_id' not in session:
        flash("Please login first!", "warning")
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books WHERE id NOT IN (SELECT book_id FROM issued_books WHERE return_date IS NULL)').fetchall()
    conn.close()
    return render_template('user_issue_books.html', books=books)
@app.route('/user/return/<int:issue_id>')
def return_issued_book(issue_id):

    if 'user_id' not in session:
        flash("Please login first!", "warning")
        return redirect(url_for('login'))

    return_date = datetime.now().date()
    conn = get_db_connection()
    issue = conn.execute('SELECT * FROM issued_books WHERE id = ? AND user_id = ?', (issue_id, session['user_id'])).fetchone()

    if issue:
        due_date = datetime.strptime(issue['due_date'], '%Y-%m-%d').date()
        days_late = (return_date - due_date).days
        fine = max(0, days_late * 10)  # ₹10 per day late

        conn.execute('''
            UPDATE issued_books 
            SET returned_date = ?, fine = ? 
            WHERE id = ?
        ''', (return_date, fine, issue_id))
        conn.commit()
        conn.close()

        flash(f'Book returned successfully! Fine: ₹{fine}', 'success')
    else:
        flash('Invalid book or permission denied.', 'danger')
        conn.close()

    return redirect(url_for('user_dashboard'))


@app.route('/user/issue/<int:book_id>')
def issue_book_handler(book_id):
    if 'user_id' not in session:
        flash("Please login first!", "warning")
        return redirect(url_for('login'))

    issue_date = datetime.now().date()
    due_date = issue_date + timedelta(days=14)  # 2 weeks from issue

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO issued_books (user_id, book_id, issue_date, due_date) VALUES (?, ?, ?, ?)',
        (session['user_id'], book_id, issue_date, due_date)
    )
    conn.commit()
    conn.close()

    flash('Book issued successfully!', 'success')
    return redirect(url_for('issue_books_page'))
@app.route('/my-books')
def user_issued_books():
    if 'user_id' not in session:
        flash('Please login to continue', 'danger')
        return redirect(url_for('login_user'))

    conn = get_db_connection()
    user_id = session['user_id']
    books = conn.execute('''
        SELECT b.title, b.author, i.issue_date, i.return_date, i.fine
        FROM issued_books i
        JOIN books b ON i.book_id = b.id
        WHERE i.user_id = ?
    ''', (user_id,)).fetchall()
    conn.close()
    return render_template('my_books.html', books=books)
@app.route('/borrow', methods=['POST'])
def borrow_book():
    if 'user_id' not in session:
        flash("Please login to borrow a book.", "danger")
        return redirect(url_for('user_login'))

    user_id = session['user_id']
    book_id = request.form['book_id']
    issue_date = datetime.now().date()
    due_date = issue_date + timedelta(days=7)

    conn = get_db_connection()

    # Check if already issued
    existing = conn.execute('SELECT * FROM issued_books WHERE user_id = ? AND book_id = ? AND return_date IS NULL', (user_id, book_id)).fetchone()
    if existing:
        flash("You already borrowed this book.", "warning")
    else:
        conn.execute('INSERT INTO issued_books (user_id, book_id, issue_date, due_date) VALUES (?, ?, ?, ?)',
                     (user_id, book_id, issue_date, due_date))
        conn.commit()
        flash("Book borrowed successfully! Return within 7 days to avoid fine.", "success")
    
    conn.close()
    return redirect(url_for('user_dashboard'))

# -------------------- LOGOUT --------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('admin', None)
    flash('Logged out successfully!', 'info')
    return redirect(url_for('home'))

# Initialize DB, seed books and run app
if __name__ == '__main__':
    init_db()
    seed_sample_books()
    create_issued_books_table()
    app.run(debug=True)
