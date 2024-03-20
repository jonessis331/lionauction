import sqlite3
import csv
import hashlib

def get_db_connection():
    conn = sqlite3.connect('lionauction.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS Users
                 (email TEXT PRIMARY KEY, password TEXT NOT NULL);''')

    c.execute('''CREATE TABLE IF NOT EXISTS Notifications (
                    Notification_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Listing_ID INTEGER,
                    User_Email TEXT,
                    Message TEXT,
                    Seen INTEGER DEFAULT 0
                    );''')

    c.execute('''CREATE TABLE IF NOT EXISTS Address
                    (address_id TEXT PRIMARY KEY, zipcode INT NOT NULL, street_num INT NOT NULL, 
                    street_name TEXT NOT NULL);''')

    c.execute('''CREATE TABLE IF NOT EXISTS Auction_Listings
                       (Seller_Email TEXT NOT NULL, Listing_ID INT NOT NULL,Category TEXT NOT NULL,Auction_Title TEXT NOT NULL,
                       Product_Name TEXT NOT NULL,Product_Description TEXT NOT NULL,Quantity INT NOT NULL,
                       Reserve_Price INT NOT NULL ,Max_bids INT NOT NULL, Status INT NOT NULL, 
                       PRIMARY KEY (Seller_Email, Listing_ID),
                       FOREIGN KEY (seller_email) REFERENCES Sellers (email),
                       FOREIGN KEY (category) REFERENCES Categories (category_name));''')

    c.execute('''CREATE TABLE IF NOT EXISTS Bidders
                           (email TEXT PRIMARY KEY,first_name TEXT NOT NULL,last_name TEXT NOT NULL,gender TEXT NOT NULL,age INT NOT NULL,
                            home_address_id TEXT NOT NULL,major TEXT NOT NULL,
                            FOREIGN KEY (email) REFERENCES Users(email),
                            FOREIGN KEY (home_address_id) REFERENCES Address (address_ID));''')

    c.execute('''CREATE TABLE IF NOT EXISTS Helpdesk 
                        (email TEXT PRIMARY KEY, position TEXT NOT NULL, FOREIGN KEY (email) REFERENCES Users (email));''')

    c.execute('''CREATE TABLE IF NOT EXISTS Requests 
                        (request_id INTEGER PRIMARY KEY, sender_email TEXT NOT NULL, helpdesk_staff_email TEXT NOT NULL, request_type TEXT NOT NULL,
                        request_desc TEXT NOT NULL, request_status INTEGER NOT NULL CHECK(request_status IN (0, 1)), FOREIGN KEY (sender_email) REFERENCES Users (email),
                        FOREIGN KEY (helpdesk_staff_email) REFERENCES Helpdesk (email));''')

    c.execute('''CREATE TABLE IF NOT EXISTS Zipcode_Info (
                        zipcode TEXT PRIMARY KEY, city TEXT NOT NULL, state TEXT NOT NULL);''')

    c.execute('''CREATE TABLE IF NOT EXISTS Credit_Cards (
                        credit_card_num TEXT PRIMARY KEY, card_type TEXT NOT NULL, expire_month INTEGER NOT NULL, expire_year INTEGER NOT NULL,
                        security_code INTEGER NOT NULL, owner_email TEXT NOT NULL, FOREIGN KEY (owner_email) REFERENCES Bidders (email));''')

    c.execute('''CREATE TABLE IF NOT EXISTS Sellers (
                        email TEXT PRIMARY KEY,
                        bank_routing_number TEXT NOT NULL,
                        bank_account_number TEXT NOT NULL,
                        balance REAL NOT NULL,
                        FOREIGN KEY (email) REFERENCES Bidders (email)
                        );''')

    c.execute('''CREATE TABLE IF NOT EXISTS Local_Vendors (
                email TEXT PRIMARY KEY,
                business_name TEXT NOT NULL,
                business_address_id INTEGER NOT NULL,
                customer_service_phone_number TEXT NOT NULL,
                FOREIGN KEY (email) REFERENCES Sellers (email),
                FOREIGN KEY (business_address_id) REFERENCES Address (address_ID)
                );''')

    c.execute('''CREATE TABLE IF NOT EXISTS Categories (
                parent_category TEXT NOT NULL,
                category_name TEXT PRIMARY KEY
                );''')

    c.execute('''CREATE TABLE IF NOT EXISTS Bids (
                bid_id INTEGER PRIMARY KEY,
                seller_email TEXT NOT NULL,
                listing_id INTEGER NOT NULL,
                bidder_email TEXT NOT NULL,
                bid_price REAL NOT NULL,
                FOREIGN KEY (seller_email, listing_id) REFERENCES Auction_Listings (seller_email, listing_id),
                FOREIGN KEY (bidder_email) REFERENCES Bidders (email)
                );''')

    c.execute('''CREATE TABLE IF NOT EXISTS Transactions (
                transaction_id INTEGER PRIMARY KEY,
                seller_email TEXT NOT NULL,
                listing_id INTEGER NOT NULL,
                buyer_email TEXT NOT NULL,
                date TEXT NOT NULL,
                payment REAL NOT NULL,
                FOREIGN KEY (seller_email, listing_id) REFERENCES Auction_Listings (seller_email, listing_id),
                FOREIGN KEY (buyer_email) REFERENCES Bidders (email)
                );''')

    c.execute('''CREATE TABLE IF NOT EXISTS Rating (
                bidder_email TEXT NOT NULL,
                seller_email TEXT NOT NULL,
                date TEXT NOT NULL,rating INTEGER NOT NULL,
                rating_desc TEXT,
                PRIMARY KEY (bidder_email, seller_email, date),
                FOREIGN KEY (bidder_email) REFERENCES Bidders (email),
                FOREIGN KEY (seller_email) REFERENCES Sellers (email))
                ;''')





    conn.commit()
    return(conn)

def import_csv(conn):
    with open('data/Users.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)
        for row in reader:
            email, password = row
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            conn.execute("INSERT OR IGNORE INTO Users (email, password) VALUES (?, ?)", (email, hashed_password))
            conn.commit()

            c = conn.cursor()
            c.execute("SELECT * FROM Users WHERE email=?", (email,))
            inserted_row = c.fetchone()
    with open('data/Address.csv', 'r') as addrFile:
        reader = csv.reader(addrFile, delimiter = ',')
        next(reader)
        for row in reader:
            address_id, zipcode, street_num, street_name = row
            conn.execute("INSERT OR IGNORE INTO Address (address_id, zipcode, street_num, street_name) VALUES (?,?,?,?)",
                        (address_id, zipcode, street_num, street_name))
            conn.commit()
    with open('data/Auction_Listings.csv', 'r') as auctListFile:
        reader = csv.reader(auctListFile, delimiter = ',')
        next(reader)
        for row in reader:
            Seller_Email, Listing_ID, Category, Auction_Title, Product_Name, Product_Description, Quantity, Reserve_Price, Max_bids, Status = row
            conn.execute("INSERT OR IGNORE INTO Auction_Listings (Seller_Email,Listing_ID,"
                         "Category,Auction_Title,Product_Name,Product_Description,"
                         "Quantity,Reserve_Price,Max_bids,Status) VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (Seller_Email, Listing_ID, Category, Auction_Title, Product_Name,
                         Product_Description, Quantity, Reserve_Price, Max_bids, Status))
            conn.commit()
    with open('data/Bidders.csv', 'r') as bidFile:
        reader = csv.reader(bidFile, delimiter = ',')
        next(reader)
        for row in reader:
            email, first_name, last_name, gender, age, home_address_id, major = row
            conn.execute("INSERT OR IGNORE INTO Bidders (email,first_name,last_name,gender,age,home_address_id,major) VALUES (?,?,?,?,?,?,?)",
                        (email,first_name,last_name,gender,age,home_address_id,major))
            conn.commit()

    with open('data/Helpdesk.csv', 'r') as helpdeskFile:
        reader = csv.reader(helpdeskFile, delimiter=',')
        next(reader)
        for row in reader:
            email, position = row
            conn.execute("INSERT OR IGNORE INTO Helpdesk (email, position) VALUES (?, ?)",
                         (email, position))
            conn.commit()

    with open('data/Requests.csv', 'r') as requestsFile:
        reader = csv.reader(requestsFile, delimiter=',')
        next(reader)
        for row in reader:
            request_id, sender_email, helpdesk_staff_email, request_type, request_desc, request_status = row
            conn.execute("INSERT OR IGNORE INTO Requests (request_id, sender_email, helpdesk_staff_email, request_type, request_desc, request_status) VALUES (?, ?, ?, ?, ?, ?)",
                        (request_id, sender_email, helpdesk_staff_email, request_type, request_desc, request_status))
            conn.commit()

    with open('data/Zipcode_Info.csv', 'r') as zipcodeFile:
        reader = csv.reader(zipcodeFile, delimiter=',')
        next(reader)
        for row in reader:
            zipcode, city, state = row
            conn.execute("INSERT OR IGNORE INTO Zipcode_Info (zipcode, city, state) VALUES (?, ?, ?)",
                         (zipcode, city, state))
            conn.commit()

    with open('data/Credit_Cards.csv', 'r') as cardsFile:
        reader = csv.reader(cardsFile, delimiter=',')
        next(reader)
        for row in reader:
            credit_card_num, card_type, expire_month, expire_year, security_code, owner_email = row
            conn.execute("INSERT OR IGNORE INTO Credit_Cards (credit_card_num, card_type, expire_month, expire_year, security_code, owner_email) VALUES (?, ?, ?, ?, ?, ?)",
                        (credit_card_num, card_type, expire_month, expire_year, security_code, owner_email))
            conn.commit()

    with open('data/Sellers.csv', 'r') as sellersFile:
        reader = csv.reader(sellersFile, delimiter=',')
        next(reader)
        for row in reader:
            email, bank_routing_number, bank_account_number, balance = row
            conn.execute("INSERT OR IGNORE INTO Sellers (email, bank_routing_number, bank_account_number, balance) VALUES (?, ?, ?, ?)",
                        (email, bank_routing_number, bank_account_number, balance))
            conn.commit()

    with open('data/Local_Vendors.csv', 'r') as vendorsFile:
        reader = csv.reader(vendorsFile, delimiter=',')
        next(reader)
        for row in reader:
            email, business_name, business_address_id, customer_service_phone_number = row
            conn.execute("INSERT OR IGNORE INTO Local_Vendors (email, business_name, business_address_id, customer_service_phone_number) VALUES (?,?,?,?)",
                         (email, business_name, business_address_id, customer_service_phone_number))
        conn.commit()

    with open('data/Categories.csv', 'r') as categoriesFile:
        reader = csv.reader(categoriesFile, delimiter=',')
        next(reader)
        for row in reader:
            parent_category, category_name = row
            conn.execute("INSERT OR IGNORE INTO Categories (parent_category, category_name) VALUES (?, ?)",
                     (parent_category, category_name))
        conn.commit()

    with open('data/Bids.csv', 'r') as bidsFile:
        reader = csv.reader(bidsFile, delimiter=',')
        next(reader)
        for row in reader:
            bid_id, seller_email, listing_id, bidder_email, bid_price = row
            conn.execute("INSERT OR IGNORE INTO Bids (bid_id, seller_email, listing_id, bidder_email, bid_price) VALUES (?, ?, ?, ?, ?)",
                (bid_id, seller_email, listing_id, bidder_email, bid_price))
            conn.commit()

    with open('data/Transactions.csv', 'r') as transactionsFile:
        reader = csv.reader(transactionsFile, delimiter=',')
        next(reader)
        for row in reader:
            transaction_id, seller_email, listing_id, buyer_email, date, payment = row
            conn.execute("INSERT OR IGNORE INTO Transactions (transaction_id, seller_email, listing_id, buyer_email, date, payment) VALUES (?, ?, ?, ?, ?, ?)",
                (transaction_id, seller_email, listing_id, buyer_email, date, payment))
            conn.commit()

    with open('data/Ratings.csv', 'r') as ratingFile:
        reader = csv.reader(ratingFile, delimiter=',')
        next(reader)
        for row in reader:
            bidder_email, seller_email, date, rating, rating_desc = row
            conn.execute("INSERT OR IGNORE INTO Rating (bidder_email, seller_email, date, rating, rating_desc) VALUES (?, ?, ?, ?, ?)",
                (bidder_email, seller_email, date, rating, rating_desc))
            conn.commit()





if __name__ == '__main__':
    conn = get_db_connection()
    init_db()
    import_csv(conn)
    conn.close()