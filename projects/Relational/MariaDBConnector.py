class MariaDBConnector:

    def __init__(self, username, password):
        self.username = username
        self.password = password

    # TODO: da continuare a sviluppare
    def add_data(first_name, last_name):
        try:
            statement = "INSERT INTO employees (first_name,last_name) VALUES (%s, %s)"
            data = (first_name, last_name)
            cursor.execute(statement, data)
            connection.commit()
            print("Successfully added entry to database")
        except database.Error as e:
            print(f"Error adding entry to database: {e}")