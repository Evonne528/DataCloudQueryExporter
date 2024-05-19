import gradio as gr
from salesforcecdpconnector.connection import SalesforceCDPConnection
import csv
import io
import tempfile

# Global variable to hold the connection
global conn
conn = None

def DC_Connection(login_url, user_name, password, client_id, client_secret):
    global conn
    try:
        if not conn:
            conn = SalesforceCDPConnection(
                login_url, 
                user_name, 
                password, 
                client_id, 
                client_secret
            )
        token, instance_url = conn.authentication_helper.get_token()
        if token:
            return f"Connected Successfully to {instance_url} with token: {token}"
        else:
            return "Failed to connect: No token retrieved."
    except Exception as e:
        return f"An error occurred: {str(e)}"

def DC_Query(sql):
    global conn
    if not conn:
        return "No active connection. Please connect first."
    try:
        cur = conn.cursor()
        cur.execute(sql)
        results = cur.fetchall()

        # Creating a temporary file to store the CSV data
        temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w+", suffix=".csv")
        writer = csv.writer(temp_file)

        # Assuming the first row consists of column headers
        if results:
            writer.writerow([desc[0] for desc in cur.description])  # column headers
            writer.writerows(results)  # query results

        temp_file.seek(0)  # rewind to the beginning of the file

        return temp_file.name  # return the path to the temporary file
    except Exception as e:
        return f"Error executing query: {str(e)}"

with gr.Blocks() as demo:
    with gr.Tab("DC Connection"):
        login_url = gr.Textbox(label="Login URL")
        user_name = gr.Textbox(label="User Name")
        password = gr.Textbox(label="Password", type="password")
        client_id = gr.Textbox(label="Client ID", type="password")
        client_secret = gr.Textbox(label="Client Secret", type="password")
        
        button = gr.Button("Connect")
        
        output_info = gr.Textbox(label="Connection Status")
    with gr.Tab("DC Query"):
        sql = gr.Textbox(label="SQL", lines=4)
        file_output = gr.File()
        query_button = gr.Button("Query")

    button.click(DC_Connection, inputs=[login_url, user_name, password, client_id, client_secret], outputs=output_info)
    query_button.click(DC_Query, inputs=[sql], outputs=[file_output])

if __name__ == "__main__":
    demo.launch(share=True)