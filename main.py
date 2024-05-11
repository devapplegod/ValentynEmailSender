import time

import pandas as pd
import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Tuto funkci jsem úvodně použil pro převedení MySQL databáze do Excelu (abych mohl jednoduše vymazat nevhodné valentýnky,
# jejichž riziko vzrostlo, vzhledem k tomu, že se nacházíme na internetu :D)
def data_to_excel():
    db_config = {
        'host': 'db_server',
        'user': 'username',
        'password': 'heslo',
        'database': 'mysqldatabaze',
    }
    conn = mysql.connector.connect(**db_config)
    table_name = 'valentynky'
    query = f'SELECT * FROM {table_name}'
    df = pd.read_sql_query(query, conn)
    conn.close()
    excel_file_path = 'output_data2.xlsx'
    df.to_excel(excel_file_path, index=False)
    print(f'Data exported to {excel_file_path} successfully!')
    # unique_names_count = df['Name'].nunique()
    # print(f'The number of unique names in the database is: {unique_names_count}')

# Odešle email
def send_email(recipient_email, subject, body_text):
    sender_email = "duchporgu@porg.fun"
    sender_password = "heslo"
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(body_text, "plain"))

    with smtplib.SMTP("smtp.titan.email", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())

# Vytvoří emaily z valentýnek v excelu - když dostal človek více valentýnek, odešlou se mu v jednom emailu
def generate_emails_from_excel(path):
    df = pd.read_excel(path)
    email_messages_dict = {}
    for index, row in df.iterrows():
        email = row['Email']
        message = row['Message']

        if email not in email_messages_dict:
            email_messages_dict[email] = [message]
        else:
            email_messages_dict[email].append(message)

    email_texts = {}
    filler = "----------------------------------------------------------------------------"

    for email, messages in email_messages_dict.items():
        text = f"Ahoj,\n\npřeji ti šťastný Valentýn a hezké prázdniny.\n\nS láskou,\n\nDuch PORGu ❤\n\n\nníže najdeš všechny tobě adresované anonymní zprávy:\n{filler}"
        for message in messages:
            text = text + f"\n\n{message}\n\n{filler}"
        email_texts[email] = text

    return email_texts


checkup_address = "bednarjosef@porg.cz"
excel_file_path = 'output_data2.xlsx' ## Excel se všemi valentýnkami uloženými ve formátu [Sender_Name; Recipient_Email; Recipient_Class; Message; Datetime]
email_dict = generate_emails_from_excel(excel_file_path)
# for email, text in email_dict.items():
#     print(f"{email}\n")
#     print(f"{text}\n")

# Začne odesílat všech CCA 200 emailů v 30 sekundových intervalech (pro zabránění spamu a zablokování nově vytvořeného email účtu) - tento kód jsem pustil na VPS a ne na PC.
def send_emails_dict_interval(dictionary, interval, checkup_email_address):
    # to_email = 'josef.bednar@mensa.cz'
    send_email(checkup_email_address, "Start", f"Successfully initiated email sending.")
    for idx, (recipient_email, message) in enumerate(dictionary.items(), start=1):
        send_email(recipient_email, "Valentýn <3", message)
        print(f"Email sent to {recipient_email} with message: {message}")
        if idx % 30 == 0:
            send_email(checkup_email_address, "Checkup", f"Checkup email - {idx} emails sent.")
            print(f"Checkup email sent after {idx} emails.")
        time.sleep(interval)

    send_email(checkup_address, "Distribution finished", f"All emails sent successfully.")
    print("Final checkup email sent, process finished.")


send_emails_dict_interval(email_dict, 45, checkup_address)
