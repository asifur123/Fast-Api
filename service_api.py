from flask import Flask, jsonify,request
import psycopg2
import cx_Oracle  # You can use any database library here

app = Flask(__name__)

@app.route('/api/service_list', methods=['GET'])
def get_data():
    try:
        # Establish a database connection (you may need to replace this with your database connection)
        ip = '20.207.91.194'
        port = 15022
        SID = 'PRHLIVE'
        dsn_tns = cx_Oracle.makedsn(ip, port, SID)
        conn = cx_Oracle.connect('prhlivero', 'prhlivero421', dsn_tns)
        cursor = conn.cursor()

        conn1 = psycopg2.connect(database="eptdb", user="eptdb", password="v8zr5QNN7MkDZ6cJVX6AGYsz", host="3.6.187.160",
                        port="4523")
        cur1 = conn1.cursor()

        sql1 = '''
        SELECT token
            FROM common.p3r_access_token
            where id = 36
            and is_active = true;
        '''

        cur1.execute(sql1)
        rows1 = cur1.fetchall()
        headers = request.headers
        s_api_key = headers.get("auth")

        if s_api_key == rows1[0][0]:

            # Replace with your SQL query
            sql_query = """
                select
        distinct tt.SERVICE_MASTER_ID,
        (tt.service_name) SERVICE_NAME,

        case
            when LOWER(tt.service_code) like '%b2b%' then 'B2B'
            else 'B2C'
        end as Category
    from
        (
        select
            s.service_name service_name,
            s.SERVICE_MASTER_ID,
            t.totalcharges amount,
            t.tariffversion my_version,
            s.service_type,
            s.service_code,
            s.is_active,
            s.est_duration,
            s.SPECIAL_INSTRUCTION
        from
            PRHLIVE.TARIFF t
        left outer join PRHLIVE.SERVICEMASTER s on
            t.service_id = s.service_master_id
        where
            s.service_name is not null
            and s.is_active = 'Y') tt
    inner join(
        select
            pp.service_name my_service,
            max(pp.my_version) as maximum_version
        from
            (
            select
                s.service_name service_name,
                t.totalcharges amount,
                t.tariffversion my_version,
                s.service_type
            from
                PRHLIVE.TARIFF t
            left outer join PRHLIVE.SERVICEMASTER s on
                t.service_id = s.service_master_id
            where
                s.service_name is not null
                and s.is_active = 'Y') pp
        group by
            pp.service_name) groupedtt on
        tt.service_name = groupedtt.my_service
        and tt.my_version = groupedtt.maximum_version
    where
        tt.service_type = 115

    order by

        tt.service_name
            """

            cursor.execute(sql_query)
            results = cursor.fetchall()

            # Define the keys for the JSON response
            keys = ["service_id", "service_name", "category"]

            # Convert the results to a list of dictionaries
            data = [dict(zip(keys, row)) for row in results]

            # Close the database connection
            conn.close()

            return jsonify(data)
        else:
            raise Exception('You are not authorised to access this api with the key you provided!')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
