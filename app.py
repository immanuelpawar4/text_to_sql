from flask import *
import pandas as pd
import sqlite3
import os
from werkzeug.utils import secure_filename
from sqlConnectionClass import Columns
from flask_cors import CORS, cross_origin
import glob
import logger_test as logger
import requests
import json

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*", "methods": ["GET", "POST"]}})
app.config['CORS_HEADERS'] = 'Content-Type'
df_columns = Columns()


@app.route('/')
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def main():
    return render_template("upload.html")


@app.route('/upload', methods=['POST', 'GET'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
@cross_origin(supports_credentials=True)
def uploadingFileAndCreatingDb():
    try:
        files = glob.glob('./files/*')
        for f in files:
            os.remove(f)
        file = request.files['Data']
        filename = secure_filename(file.filename)
        file.save(os.path.join('./files/', filename))
        if filename.split('.')[-1] == 'xls' or filename.split('.')[-1] == 'xlsx':
            df = pd.read_excel(os.path.join('./files/', filename))

        elif filename.split('.')[-1] == 'csv':
            df = pd.read_csv(os.path.join('./files/', filename), encoding='latin1')
        df_columns.storeColumns(df.columns)
        conn = sqlite3.connect('global_sales.sqlite')
        df.to_sql('sales_data', conn, if_exists='replace', index=False)
        logger.logging.info("--------------------------------")
        return {'statusCode': 200,
                'body': "File Uploaded Successfully",
                'columns': json.dumps(df.columns.tolist()),
                'headers': {
                    'Access-Control-Allow-Headers': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                }}
    except Exception as e:
        logger.logging.error(str(e))
        return {'statusCode': 400,
                # 'body': final_response['choices'][0]['text'],
                'body': str(e),
                'headers': {
                    'Access-Control-Allow-Headers': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                }}

    # return render_template("upload.html", message='File uploaded successfully.')


@app.route('/sql_query_response', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_response():
    text = request.args.get('promt')
    api_list = ["secret_557949fa935c-40d3-a070-d14df47cdd62", "secret_27b7d45fcce9-47b8-bb4a-7656245fae4a", "secret_8e0b822e05ff-42f7-a17c-9e3f27465c47", "secret_151e0bb9f70e-4d3c-af35-eda97963e27f", "secret_ed4c193659b1-4705-951c-80cf96d870ba"]
    try:
        print("text :", text)
        # Commit the changes and close the connection
        conn = sqlite3.connect('global_sales.sqlite')
        conn.commit()
        columns = df_columns.returnColumns()
        print(columns.tolist())
        # openai.api_key = "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"
        # response = openai.Completion.create(model="text-davinci-003",
        #                                     prompt=f"### sqllite SQL tables, with their properties:\n#\n# sales_data{tuple(columns)}\n# A query to answer: {text}\nSELECT",
        #                                     temperature=0, top_p=1.0, frequency_penalty=0.0,
        #                                     presence_penalty=0.0, stop=["#", ";"])

        # Define API endpoint URL
        url = "https://app.text2sql.co/api/v1/sql"
        query = ""
        body = {
            "query": text,
            "dialect": "ansi_sql",
            "tables": [
                {
                    "table_name": 'sales_data_sample',
                    "columns": columns.tolist()
                }
            ]
        }
        for api in api_list:
            api_key = api
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            response = requests.post(url, headers=headers, json=body)
            if response.status_code == 200:
                query = response.json()['data']['sql']
                query = query.replace('undefined', "sales_data")
                break
            else:
                print("api key : ", api_key)
                print(f"Request failed with error code {response.status_code}: {response.text}")
                continue

        # output = response.choices[0].text.strip()
        # print(output)
        # query = 'Select' + response['choices'][0]['text'] + ';'
        if query == "":
            raise Exception("Limit exceeded")
        print("query", query)
        cur = conn.cursor()
        cur.execute(query)
        columns = tuple(row[0] for row in cur.description)
        query_response = dict()
        query_response['columns'] = columns
        query_res = cur.fetchall()
        print("query_res", query_res)
        query_response['values'] = query_res
        print("query_response", query_response)
        print("--------------------------------------------------------------")

        my_dict = query_response
        for key, values in my_dict.items():
            new_values = []
            for value in values:
                if isinstance(value, str):
                    new_value = value.replace('\xa0', ' ')
                    new_value = new_value.replace('\t', ' ')
                else:
                    new_value = value
                new_values.append(new_value)
            my_dict[key] = tuple(new_values)
        print(my_dict)
        data_dict = my_dict

        # df = pd.DataFrame(data_dict['values'], columns=data_dict['columns'])
        # if len(df)>4:
        #     df = df[:4]
        # remove = ['!', '@', '#', '%', '^', '&', '*', '\n', '0\xa02.', 'b']
        #
        # model_engine = "text-davinci-002"
        # text = " ".join(df.astype(str).agg(" ".join, axis=1).tolist())
        # print("text", text)
        # prompt = f"Please summarize the following dataframe: {text}"
        # completions = openai.Completion.create(
        #     engine=model_engine, prompt=prompt,
        #     max_tokens=500, n=1,
        #     stop=None,
        #     temperature=0.7, )
        # message = completions.choices[0].text.strip()
        # for char in remove:
        #     message = message.replace(char, '')
        # summary = message

        # Get the column names and values from the data dictionary
        column_names = data_dict['columns']
        data_values = data_dict['values']
        array_result = []
        array_result.append(column_names)
        array_result.extend(data_values)

        # model_engine = "davinci"
        # prompt = f"Summarize the following : {query_response}"
        #
        # # Generate summary using OpenAI API
        # summary_response = openai.Completion.create(
        #     engine=model_engine,
        #     prompt=prompt,
        #     n=1,
        #     stop=None,
        #     temperature=0.5,
        # )
        #
        # # Print summary
        # summary = summary_response.choices[0].text.strip()
        # print(summary)
        # output = {
        #     "question": text,
        #     "answer": summary
        # }
        logger.logging.info("--------------------------------")
        return {'statusCode': 200,
                # 'body': final_response['choices'][0]['text'],
                'body': array_result,
                'prompt': text,
                'headers': {
                    'Access-Control-Allow-Headers': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                }}
    except Exception as e:
        logger.logging.error(str(e))
        return {'statusCode': 400,
                # 'body': final_response['choices'][0]['text'],
                'body': str(e),
                'prompt': text,
                'headers': {
                    'Access-Control-Allow-Headers': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                }}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
