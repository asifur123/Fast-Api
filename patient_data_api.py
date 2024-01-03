from flask import Flask, request, jsonify
import cx_Oracle

app = Flask(__name)

# Replace these values with your Oracle database connection details
db_config = {
    "user": "your_username",
    "password": "your_password",
    "dsn": "your_oracle_dsn"
}

@app.route('/get_patient_data', methods=['GET'])
def get_patient_data():
    try:
        # Get the patient_id from the request parameters
        get_patient_id = request.args.get('patient_id')

        if get_patient_id is None:
            return jsonify({"error": "patient_id parameter is required"}), 400

        # Connect to the Oracle database
        connection = cx_Oracle.connect(db_config["user"], db_config["password"], db_config["dsn"])

        # Create a cursor object
        cursor = connection.cursor()

        # SQL query
        query = """
        SELECT p.PATIENT_ID, p.MRNO, p.PATIENTNAME, 
               CASE p.GENDERID WHEN 1 THEN 'Male' ELSE 'Female' END AS GENDER, 
               p.MOBILENO, p.EMAIL, TO_CHAR(p.DOB, 'dd-MON-YYYY') AS DOB, 
               pi2.PATIDNO AS PASSPORT_NO, pi2.ISSUING_AUTHORITY 
        FROM PRHLIVE.PATIENT p 
        LEFT JOIN PRHLIVE.PATIENT_IDENTIFICATION pi2 
        ON p.PATIENT_ID = pi2.PATIENT_ID 
        WHERE p.PATIENT_ID = :get_patient_id
        """

        # Execute the query with the patient ID parameter
        cursor.execute(query, get_patient_id=get_patient_id)

        # Fetch the result
        result = cursor.fetchone()

        # Close the cursor and the database connection
        cursor.close()
        connection.close()

        if result is None:
            return jsonify({"error": "Patient data not found"}), 404

        # Convert the result to a JSON format
        response_data = {
            "patient_data": result
        }

        return jsonify(response_data)

    except cx_Oracle.Error as error:
        return jsonify({"error": f"Error fetching data from Oracle: {error}"}), 500

if _name_ == '_main_':
    app.run(debug=True)
