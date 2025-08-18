from django.http import JsonResponse
from exchangelib import Credentials, Account, Configuration, DELEGATE, NTLM


def check_email(login, password):
    # Optional: you can secure this endpoint with login_required or token authentication

    try:
        _login = login.split('@')[0]
        username = f'apa.kz\\{_login}'
        # password = '9xWF9TZ+'
        email_address = login
        exchange_server = 'mail.apa.kz'

        credentials = Credentials(username=username, password=password)
        config = Configuration(server=exchange_server, credentials=credentials, auth_type=NTLM)
        account = Account(primary_smtp_address=email_address, config=config, autodiscover=False, access_type=DELEGATE)

        unread_emails = account.inbox.filter(is_read=False).order_by('-datetime_received')[:10]

        email_data = []
        for msg in unread_emails:
            email_data.append({
                'subject': msg.subject,
                'from': msg.sender.email_address if msg.sender else 'Unknown',
                'received': msg.datetime_received.strftime('%Y-%m-%d %H:%M:%S'),
                #'body': str(msg.body)[:500],  # limit size
                'body': str(msg.body),
            })

        #return JsonResponse({'emails': email_data})
        return email_data

    except Exception as e:
        #return JsonResponse({'error': str(e)}, status=500)
        return None