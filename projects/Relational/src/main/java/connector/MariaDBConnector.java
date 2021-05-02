package connector;

import java.sql.*;

public class MariaDBConnector {

    public MariaDBConnector() {
    }

    static final String DB_URL = "jdbc:mariadb://localhost:3306/test";

    //  Database credentials
    static final String USER = "root";
    static final String PASS = "rootpass";

    public static void main( String[] args ) throws SQLException {
        //create connection for a server installed in localhost, with a user "root" with no password
        try (Connection conn = DriverManager.getConnection(DB_URL, USER, PASS)) {
            // create a Statement
            try (Statement stmt = conn.createStatement()) {
                //execute query
//                try (ResultSet rs = stmt.executeQuery("SELECT 'Hello World!'")) {
//                    //position result to first
//                    rs.first();
//                    System.out.println(rs.getString(1)); //result is "Hello World!"
//                }
                System.out.println("TEST");
                try (ResultSet rs = stmt.executeQuery("SELECT * FROM EMOSNANGER")) {
                    //position result to first
                    rs.last();
                    //rs.first();
                    System.out.println(rs.getString(1)); //result is "Hello World!"
                }
            }
        }
    }
}
