import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import EMAIL_HOST, SENDER, EMAIL_KEY


def send_email(url, receiver):
    message = f"您的MV已经合成完毕，请点击以下链接下载：\n{url}"
    msg = MIMEMultipart()
    msg.attach(MIMEText(message, 'plain', 'utf-8'))
    msg['Subject'] = Header("MV合成完毕", "utf-8")
    msg['From'] = Header('AI-MV')
    try:
        s = smtplib.SMTP_SSL(EMAIL_HOST, 465)
        s.login(SENDER, EMAIL_KEY)
        s.sendmail(SENDER, [receiver], msg.as_string())
        s.quit()
        print(f"邮件发送成功")
    except smtplib.SMTPException as e:
        print(e)
