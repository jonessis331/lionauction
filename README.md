<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    
</head>
<body>
    <h1>LionAuction - E-commerce and Authentication System</h1>

   <h2>Overview</h2>
    <p>
        LionAuction showcases an e-commerce and authentication system developed with Flask and SQLite, demonstrating the integration of relational database management and web application design. This project serves as a practical application of database theory, relational query languages, and internal database design concepts, including views, integrity constraints, triggers, authorization, indexing, and transactions. The primary objective of this project is to exhibit a robust and efficient Entity-Relationship (ER) database flow, underpinning the core functionalities of a SQL-based data management system. While the web interface exists, it serves primarily as a conduit for database interactions rather than as a demonstration of advanced front-end development. The simplicity of the HTML/CSS design is intentional, allowing users and stakeholders to concentrate on the effectiveness and structure of the database operations and data handling processes.
    </p>

   <h2>Project Features</h2>
    <ul>
        <li>User authentication system with hashed passwords.</li>
        <li>Relational database design reflecting Entity-Relationship models.</li>
        <li>Utilization of SQL for database interactions.</li>
        <li>Implementation of Flask to create an interactive web interface.</li>
        <li>Dynamic data exchange between web pages and the SQLite database.</li>
    </ul>

   <h2>Project Setup</h2>
    <p>
        To set up the project, ensure Python and Flask are installed on your system. Place all the necessary files within a single directory. Execute the <code>importUsers.py</code> script to initialize the database and import pre-existing user data. This setup primes the application for use and testing.
    </p>

   <h2>Running the Project</h2>
    <p>
        Start by running <code>app.py</code> to launch the Flask server. Access the application by navigating to the login page via your web browser. Test the login functionality using credentials provided within the <code>Users.csv</code> file. Upon successful login, users will be directed to a confirmation page, ensuring the authentication process is operational.
    </p>

   <h2>File Structure</h2>
    <ul>
        <li><strong><code>app.py</code></strong> The Flask server script with route definitions.</li>
        <li><strong><code>importUsers.py</code></strong> Script for initializing the database and importing users.</li>
        <li><strong><code>data/</code>:</strong> sample CSV's containing user data for the application.</li>
        <li><strong><code>templates/</code></strong> Directory containing HTML files for the web interface.</li>
    </ul>

  <h2>Usage Instructions</h2>
    <p>
        After setting up the project as described above, users can interact with the application through the web interface. User authentication is handled securely, with password hashing ensuring data protection. The web interface provides a seamless user experience, allowing for straightforward navigation through the login process and subsequent interaction with e-commerce features.
    </p>

  <h2>Advanced Topics</h2>
    <p>
        Depending on further development and expansion, advanced topics such as data storage optimization, query processing efficiency, and transaction management may also be explored to enhance the robustness and performance of the system.
    </p>



</body>
</html>
