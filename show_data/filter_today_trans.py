import pandas as pd
from pymongo import MongoClient
# import plotly
from datetime import datetime, date
from time import gmtime, strftime, localtime
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
import smtplib, ssl
import sys, os
import logging, traceback

from lib_functions import connect_mongo, read_mongo

# define log
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_DIR = DIR_PATH + '/logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
CUR_TIME = strftime("%Y_%m_%d", localtime())
logging.basicConfig(filename=f'{LOG_DIR}/{CUR_TIME}',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)


def main():
    try: 
        dog_df = read_mongo(db='dogami-database', collection='dog', host=os.getenv('MONGO_HOST', "localhost"), username="abc", password="abc") 
        trans_df = read_mongo(db='dogami-database', collection='transaction', host=os.getenv('MONGO_HOST', "localhost"), username="abc", password="abc")
    except Exception as e:
        logging.error("Error while connect mongo database")
        logging.error(e)
        logging.error(traceback.format_exc())
        return 

    try: 
        # change type to mergable
        dog_df['token_id'] = dog_df['token_id'].astype(str)
        join_df = trans_df.merge(right=dog_df, how='inner', on='token_id')

        join_df['date'] = pd.to_datetime(join_df['time_stamp']).dt.date
        join_df['date_string'] = join_df['date'].astype(str)

        today_date = date.today().strftime('%Y-%m-%d')
        # today_date = datetime(2022, 3, 29).strftime('%Y-%m-%d')
        # today_date
        today_trans = join_df[join_df['date_string']==today_date]
        output = today_trans[['date', 'token_id', 'rarity_tier', 'rarity_score', 'price', 'operation_hash', 'time_stamp', 'order_type']]
        output.reset_index(drop=True, inplace=True)
    except Exception as e:
        logging.error("Error when joining table")
        logging.error(e)
        logging.error(traceback.format_exc())
        return 

    try: 
        recipients = ['haiduong667799@gmail.com'] 
        emaillist = [elem.strip().split(',') for elem in recipients]
        msg = MIMEMultipart()
        msg['Subject'] = f"Dogami Transaction {today_date}"
        msg['From'] = 'haiduong667799@gmail.com'

        html = """\
        <html>
        <head></head>
        <body>
            {0}
        </body>
        </html>
        """.format(output.to_html())

        part1 = MIMEText(html, 'html')
        msg.attach(part1)
        logging.info("Writing email context")

        logging.info("Prepare sending email")
        with  smtplib.SMTP('smtp.gmail.com', 587) as smtpserver :
            smtpserver.starttls()
            gmail_user = 'haiduong667799@gmail.com'
            gmail_pwd = 'haiduong060799'
            smtpserver.login(gmail_user, gmail_pwd)
            logging.info("Success login email")
            smtpserver.sendmail(msg['From'], emaillist , msg.as_string())
        logging.info("Successfully send email")
    except Exception as e:
        logging.error("Error when sending email")
        logging.error(e)
        logging.error(traceback.format_exc())
        return 
        
if __name__ == '__main__':
    
    logging.info("Start program")
    logging.info("Start read data and send email")
    main()
    logging.info("Finish program")