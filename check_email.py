import imaplib

def check_email():
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('memyselfff7@gmail.com', 'sxxdgqjkuejwxzqf')  # Замени на свои данные
    mail.select('inbox')
    result, data = mail.search(None, 'SUBJECT "Ваш список задач"')
    ids = data[0].split()
    if ids:
        latest_email_id = ids[-1]
        result, data = mail.fetch(latest_email_id, '(RFC822)')
        print("Найдено письмо:", data[0][1].decode('utf-8'))
    else:
        print("Письма не найдены.")
    mail.logout()

if __name__ == "__main__":
    check_email()