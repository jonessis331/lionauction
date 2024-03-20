import sqlite3
import hashlib
from flask import Flask, render_template, request, url_for, redirect, flash, session


app = Flask(__name__)
app.secret_key = 'jonessis'



def get_db_connection():
    conn = sqlite3.connect('lionauction.db')
    conn.row_factory = sqlite3.Row
    return conn

def check_login(email, password):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM Users WHERE email=?", (email,))
    user = c.fetchone()
    if user:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if hashed_password == user[1]:
            return True
    return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if check_login(email, password):
            session["loggedInUser"] = email
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM Users WHERE email=?", (email,))

            h1 = conn.cursor()
            b1 = conn.cursor()
            s1 = conn.cursor()
            h1.execute("SELECT email FROM Helpdesk WHERE email=?", (email,))
            b1.execute("SELECT email FROM Bidders  WHERE email=?", (email,))
            s1.execute("SELECT email FROM Sellers WHERE email=?", (email,))

            helpDesk = h1.fetchone()
            bidders = b1.fetchone()
            sellers = s1.fetchone()
            user = c.fetchone()

            role = request.form['role']
            if user:
                if helpDesk and role == 'helpdesk':
                    session["userType"] = "helpDesk"
                    return redirect(url_for('helpdesk'))
                elif bidders and role == 'bidder':
                    session["userType"] = "bidder"
                    return redirect(url_for('bidder'))
                elif sellers and role == 'seller':
                    session["userType"] = "seller"
                    return redirect(url_for('seller'))

        else:
            return "Login failed"
    return render_template('login.html')

@app.route('/helpdesk')
def helpdesk():
    return "Logged in as Helpdesk!"

def row_to_dict(row):
    return {key: row[key] for key in row.keys()}

@app.route('/bidder')
def bidder():
    conn = sqlite3.connect('lionauction.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    parent_categories = c.execute("SELECT DISTINCT parent_category FROM Categories").fetchall()
    categories = c.execute("SELECT * FROM Categories").fetchall()
    listings = c.execute("SELECT * FROM Auction_Listings WHERE Status = 1").fetchall()

    parent_categories = [row_to_dict(row) for row in parent_categories]
    categories = [row_to_dict(row) for row in categories]
    listings = [row_to_dict(row) for row in listings]

    conn.close()
    return render_template('bidder.html', parent_categories=parent_categories, categories=categories, listings=listings)


@app.route('/make_payment/<int:listing_id>', methods=['GET', 'POST'])
def make_payment(listing_id):
    if request.method == 'POST':
        card_number = request.form.get('cardNumber')
        expiry_date = request.form.get('expiryDate')
        cvv = request.form.get('cvv')

        # Perform basic validation on the input fields
        if not (card_number and expiry_date and cvv):
            flash("Please fill out all fields", "error")
            return redirect(url_for('make_payment', listing_id=listing_id))

        flash("Payment has been successfully processed!", "success")
        return redirect(url_for('bidder'))

    return render_template('make_payment.html', listing_id=listing_id)


@app.route('/bidOnProduct/<int:listing_id>/<string:seller_email>', methods=['GET', 'POST'])
def bidOnProduct(listing_id, seller_email):
    conn = sqlite3.connect('lionauction.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    listingInfo = c.execute("SELECT * FROM Auction_Listings WHERE Listing_ID = ? AND Seller_Email = ?",
                            (listing_id, seller_email)).fetchone()

    user_email = session["loggedInUser"]
    if request.method == 'POST':
        highest_bid = c.execute("SELECT MAX(Bid_Price), Bidder_Email FROM Bids WHERE Listing_ID = ?", (listing_id,)).fetchone()
        highest_bid_price = float(highest_bid[0]) if highest_bid[0] is not None else float(listingInfo["Reserve_Price"].replace('$', '').strip())
        highest_bidder_email = highest_bid[1]

        if highest_bidder_email != user_email:
            new_bid = float(request.form['new_bid'])
            if new_bid >= highest_bid_price + 1:
                newBid_ID = c.execute("SELECT MAX(Bid_ID) FROM Bids").fetchone()[0] + 1
                c.execute("INSERT INTO Bids(Bid_ID,Seller_Email,Listing_ID,Bidder_Email,Bid_Price) VALUES(?,?,?,?,?)",
                          (newBid_ID, seller_email, listing_id, user_email, new_bid))
                conn.commit()
                flash('Your bid has been placed successfully!', 'success')
            else:
                flash('Your bid must be at least $1 more than the previous bid.', 'error')
        else:
            flash("You can't bid again until another bid is placed by a competitor.", 'error')

    # calculate remaining bids
    remaining_bids = max(0, listingInfo["Max_bids"] - c.execute("SELECT COUNT(*) FROM Bids WHERE Listing_ID = ?", (listing_id,)).fetchone()[0] - 1)

    highest_bid = c.execute("SELECT MAX(Bid_Price), Bidder_Email FROM Bids WHERE Listing_ID = ?", (listing_id,)).fetchone()
    highest_bid_price = float(highest_bid[0]) if highest_bid[0] is not None else float(listingInfo["Reserve_Price"].replace('$', '').strip())
    highest_bidder_email = highest_bid[1]

    conn.close()
    if remaining_bids == 0:
        # The auction has ended
        # Notify all bidders about the result
        notifyBidders(listing_id)


    return render_template('bidOnProduct.html', listingInfo=listingInfo, highest_bid_price=highest_bid_price, highest_bidder_email=highest_bidder_email, remaining_bids=remaining_bids)

def notifyBidders(listing_id):
    # Retrieve all bidders for the given listing_id
    conn = sqlite3.connect('lionauction.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    bidders = c.execute("SELECT DISTINCT Bidder_Email FROM Bids WHERE Listing_ID = ?", (listing_id,)).fetchall()
    highest_bid = c.execute("SELECT MAX(Bid_Price), Bidder_Email FROM Bids WHERE Listing_ID = ?", (listing_id,)).fetchone()
    highest_bid_price = highest_bid[0]
    highest_bidder_email = highest_bid[1]

    for bidder in bidders:
        bidder_email = bidder['Bidder_Email']
        message = f"The auction for listing ID {listing_id} has ended.\n"
        message += f"The winning bid price is ${highest_bid_price}.\n"

        if bidder_email == highest_bidder_email:
            message += "Congratulations, you have won the auction!\n"
            message += "Please visit the following link to proceed with the payment:\n"
            message += f"http://127.0.0.1:5000/payment/{listing_id}"
        else:
            message += "Unfortunately, you did not win this auction."

        # Insert the message into the database
        c.execute("INSERT INTO Notifications (Listing_ID, User_Email, Message) VALUES (?, ?, ?)",
                  (listing_id, bidder_email, message))

    conn.commit()
    conn.close()

@app.route('/notifications')
def notifications():
    user_email = session["loggedInUser"]
    conn = sqlite3.connect('lionauction.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    notifications = c.execute("SELECT * FROM Notifications WHERE User_Email = ?", (user_email,)).fetchall()

    conn.close()
    return render_template('notifications.html', notifications=notifications)

@app.route('/seller')
def seller():
    global loggedInUser
    conn = sqlite3.connect('lionauction.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    parent_categories = c.execute("SELECT DISTINCT parent_category FROM Categories").fetchall()
    categories = c.execute("SELECT * FROM Categories").fetchall()
    listings = c.execute("SELECT * FROM Auction_Listings WHERE Status = 1").fetchall()

    parent_categories = [row_to_dict(row) for row in parent_categories]
    categories = [row_to_dict(row) for row in categories]
    listings = [row_to_dict(row) for row in listings]

    user_listings = c.execute("SELECT * FROM Auction_Listings WHERE Seller_Email = ?", (session["loggedInUser"],)).fetchall()
    active_listings = [listing for listing in user_listings if listing['Status'] == 1]
    inactive_listings = [listing for listing in user_listings if listing['Status'] == 0]
    sold_listings = [listing for listing in user_listings if listing['Status'] == 2]

    conn.close()
    return render_template('seller.html', active_listings=active_listings, inactive_listings=inactive_listings,
                           sold_listings=sold_listings, parent_categories=parent_categories, categories=categories, listings=listings)



@app.route('/publish_listing', methods=['GET', 'POST'])
def publish_listing():
    if request.method == 'POST':
        # Save the new listing data to the database
        category = request.form['category']
        title = request.form['title']
        name = request.form['name']
        desc = request.form['description']
        quantity = request.form['quantity']
        reserve_price = request.form['reserve_price']
        max_bids = request.form['max_bids']
        global loggedInUser
        conn = sqlite3.connect('lionauction.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        g = c.execute("SELECT MAX(Listing_ID) FROM Auction_Listings")
        max_listing_id = g.fetchone()[0]
        newAuctionID = max_listing_id + 1
        c.execute("INSERT INTO Auction_Listings(Seller_Email,Listing_ID,Category,Auction_Title,Product_Name,Product_Description,Quantity,Reserve_Price,Max_bids,Status) VALUES(?,?,?,?,?,?,?,?,?,?)",(session["loggedInUser"], newAuctionID, category, title, name, desc, quantity, reserve_price, max_bids, 1))
        conn.commit()
        conn.close()
        return redirect(url_for('seller'))

    return render_template('publish_listing.html')


@app.route('/edit_listing/<int:listing_id>', methods=['GET', 'POST'])
def edit_listing(listing_id):
    conn = sqlite3.connect('lionauction.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Fetch the existing listing data from the database
    listing_data = c.execute("SELECT * FROM Auction_Listings WHERE Listing_ID = ?", (listing_id,)).fetchone()

    if request.method == 'POST':
        # Update the listing data in the database
        category = request.form['category']
        title = request.form['title']
        name = request.form['name']
        desc = request.form['description']
        quantity = request.form['quantity']
        reserve_price = request.form['reserve_price']
        c.execute("UPDATE Auction_Listings SET Category=?, Auction_Title=?, Product_Name=?, Product_Description=?, Quantity=?, Reserve_Price=? WHERE Listing_ID=?", (category, title, name, desc, quantity, reserve_price, listing_id))
        conn.commit()

    conn.close()
    return render_template('edit_listing.html', listing=listing_data)

@app.route('/remove_listing/<int:listing_id>', methods=['GET', 'POST'])
def remove_listing(listing_id):
    if request.method == 'POST':
        reason = request.form['reason_for_remove']
        conn = sqlite3.connect('lionauction.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("UPDATE Auction_Listings SET Reason_To_Remove=?, Status= 0 WHERE Listing_ID=?", (reason, listing_id))
        conn.commit()
        conn.close()
        return redirect(url_for('seller'))
    return render_template('remove_listing.html')

@app.route('/edit_user', methods=['GET', 'POST'])
def edit_user():
    global userType
    global loggedInUser
    if request.method == 'GET':
        conn = sqlite3.connect('lionauction.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # Get user information
        if session["userType"] == "bidder":
            userInfo = c.execute("SELECT * FROM Bidders WHERE email = ?", (session["loggedInUser"],)).fetchone()
        if session["userType"] == "seller":
            userInfo = c.execute("SELECT * FROM Sellers WHERE email = ?", (session["loggedInUser"],)).fetchone()
        elif session["userType"] == "helpDesk":
            userInfo = c.execute("SELECT * FROM Helpdesk WHERE email = ?", (session["loggedInUser"],)).fetchone()

        # Get address and credit card information
        addressInfo = c.execute("SELECT * FROM Address WHERE address_id = ?", (userInfo['home_address_id'],)).fetchone()
        creditCardInfo = c.execute("SELECT * FROM Credit_Cards WHERE Owner_email = ?", (session["loggedInUser"],)).fetchone()

        conn.close()

        user = {
            **userInfo,
            'address': f"{addressInfo['street_num']} {addressInfo['street_name']}",
            'credit_card': creditCardInfo['credit_card_num'],
            'street_num': addressInfo['street_num'],
            'street_name': addressInfo['street_name'],
            'zipcode': addressInfo['zipcode'],
            'card_type': creditCardInfo['card_type'],
            'expire_month': creditCardInfo['expire_month'],
            'expire_year': creditCardInfo['expire_year'],
            'security_code': creditCardInfo['security_code']
        }

        return render_template('edit_user.html', user=user)
    else:
        # Get the updated user information from the form
        firstname = request.form['name']
        lastname = request.form['lastname']
        age = request.form['age']
        gender = request.form['gender']
        major = request.form['major']

        street_num = request.form['street_num']
        street_name = request.form['street_name']
        zipcode = request.form['zipcode']
        credit_card = request.form['credit_card']
        card_type = request.form['card_type']
        expire_month = request.form['expire_month']
        expire_year = request.form['expire_year']
        security_code = request.form['security_code']
        # Add any other necessary form fields to get user information

        conn = sqlite3.connect('lionauction.db')

        c = conn.cursor()
        c.row_factory = sqlite3.Row


        # Update the user information in the database
        if session["userType"] == "bidder":
            user_info = c.execute("SELECT home_address_id, email FROM Bidders WHERE email = ?",
                                  (session["loggedInUser"],)).fetchone()
            c.execute("UPDATE Bidders SET first_name = ?, last_name = ?, gender = ?, age = ?, major = ?,WHERE email = ?",
                      (firstname, lastname, gender, age, major))
        elif session["userType"] == "seller":
            user_info = c.execute("SELECT home_address_id, email FROM Sellers WHERE email = ?",
                                  (session["loggedInUser"],)).fetchone()
            c.execute(
                "UPDATE Sellers SET first_name = ?, last_name = ?, gender = ?, age = ?, major = ?,WHERE email = ?",
                (firstname, lastname, gender, age, major))
        elif session["userType"] == "helpDesk":
            user_info = c.execute("SELECT home_address_id, email FROM Hekpdesk WHERE email = ?",
                                  (session["loggedInUser"],)).fetchone()


        home_address_id = user_info['home_address_id']
        owner_email = user_info['email']

        # Update the address information in the database
        c.execute("UPDATE Address SET street_num=?, street_name=?, zipcode=? WHERE address_id=?",
                  (street_num, street_name, zipcode, home_address_id))

        # Update the credit card information in the database
        c.execute(
            "UPDATE Credit_Cards SET credit_card_num=?, card_type=?, expire_month=?, expire_year=?, security_code=? WHERE Owner_email=?",
            (credit_card, card_type, expire_month, expire_year, security_code, owner_email))



        conn.commit()

        return redirect(url_for('bidder'))


@app.route('/my_bids')
def my_bids():
    conn = sqlite3.connect('lionauction.db')
    c = conn.cursor()
    c.row_factory = sqlite3.Row

    email = session["loggedInUser"]

    bids = c.execute("SELECT * FROM Bids WHERE Bidder_Email = ?", (email,)).fetchall()
    bid_list = []
    print("email:", email)  # Add this line to print the email
    print("bids:", bids)


    for bid in bids:
        auction_id = bid['Listing_ID']
        auction_listing = c.execute("SELECT * FROM Auction_Listings WHERE Listing_ID = ? and status", (auction_id,)).fetchone()
        highest_bid = c.execute("SELECT MAX(Bid_Price) as max_bid FROM Bids WHERE Listing_ID = ?", (auction_id,)).fetchone()
        bid_list.append((bid, auction_listing, highest_bid))

    conn.close()

    print("bid_list:", bid_list)

    return render_template('my_bids.html', bid_list=bid_list)



if __name__ == '__main__':
    loggedInUser = ""
    userType = ""
    app.run(debug=True)





