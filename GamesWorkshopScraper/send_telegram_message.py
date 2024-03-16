import urllib.parse
import urllib.request
from update_database import *
import os
import paramiko


def send_telegram(msg):
    # Telegram bot settings
    telegram_token = "****"
    telegram_chat_id = "****"
    msg = "".join(msg)

    msg = urllib.parse.quote(msg)
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage?chat_id={telegram_chat_id}&text={msg}"
    urllib.request.urlopen(url)


def send_update_message(data, database, item_avail_key, item_name_key, item_url_key, message_prefix, website_url):
    items_to_message = update_database(data, database, item_avail_key, item_name_key, item_url_key)

    paste_path = '/var/www/html/'
    telegram_token = "****"
    telegram_chat_id = "****"

    if items_to_message:
        message = f"{message_prefix} in stock:\n"
        for item in items_to_message:
            message += f"{item[item_name_key]}\n{website_url}{item[item_url_key]}\n"
        message = "".join(message)
        message = urllib.parse.quote(message)
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage?chat_id={telegram_chat_id}&text={message}"
        urllib.request.urlopen(url)
        copy_files_from_server(database, paste_path)
        return True
    else:
        return False


def copy_files_from_server(copy_file, paste_folder):
    hostname = '****'
    username = '****'
    password = '****'
    try:
        # Create SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the server
        client.connect(hostname=hostname, port=22, username=username, password=password)

        # Create SFTP client
        sftp = client.open_sftp()

        try:

            remote_path = os.path.join(paste_folder + copy_file)
            sftp.put("sqlite/db/" + copy_file, remote_path)
            print(f"File '{copy_file}' copied successfully!")
        except Exception as e:
            print(f"{copy_file} not copied ", str(e))
    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your credentials.")
    except paramiko.SSHException as ssh_exception:
        print("Unable to establish SSH connection:", str(ssh_exception))
    except Exception as e:
        print("An error occurred:", str(e))
        print(copy_file)
    finally:
        # Close the SFTP and SSH client
        sftp.close()
        client.close()
