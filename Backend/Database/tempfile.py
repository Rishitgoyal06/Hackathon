import sqlite3

def seed_admins():
    """Insert sample admins into Admin table (run once)."""
    connection = sqlite3.connect("school_portal.db")
    cursor = connection.cursor()

    try:
        cursor.execute('''
        INSERT OR IGNORE INTO Admin (AdminID, Name, DOB, School, Gender, Email, Phone, Password) VALUES
        (1, 'Rohit Sharma', '1980-03-15', 'Delhi Public School', 'Male', 'rohit.sharma@dps.edu', '9876543210', 'admin123'),
        (2, 'Priya Mehta', '1985-07-22', 'Shemford Futuristic School', 'Female', 'priya.mehta@shemford.edu', '9876504321', 'priya@85'),
        (3, 'Amit Verma', '1979-11-10', 'St. Francis Academy', 'Male', 'amit.verma@stfrancis.edu', '9812345678', 'amit#1979'),
        (4, 'Neha Singh', '1990-01-05', 'Parul University School', 'Female', 'neha.singh@parul.edu', '9898989898', 'nehaSingh90'),
        (5, 'Rajesh Kumar', '1975-05-30', 'Amity International School', 'Male', 'rajesh.kumar@amity.edu', '9123456789', 'rajesh@75'),
        (6, 'Sneha Patel', '1988-09-12', 'Kendriya Vidyalaya', 'Female', 'sneha.patel@kv.edu', '9765432109', 'sneha#1988'),
        (7, 'Anil Joshi', '1982-04-18', 'Modern School', 'Male', 'anil.joshi@modern.edu', '9911223344', 'anil@82'),
        (8, 'Kavita Sharma', '1987-12-25', 'DAV Public School', 'Female', 'kavita.sharma@dav.edu', '9988776655', 'kavita25'),
        (9, 'Suresh Reddy', '1978-08-08', 'Oakridge International School', 'Male', 'suresh.reddy@oakridge.edu', '9090909090', 'suresh@1978'),
        (10, 'Meena Nair', '1983-06-19', 'National Public School', 'Female', 'meena.nair@nps.edu', '9345678901', 'meena#83')
        ''')
        connection.commit()
        print("✅ Admins seeded successfully!")
    except sqlite3.IntegrityError as e:
        print(f"❌ Database Error: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    seed_admins()