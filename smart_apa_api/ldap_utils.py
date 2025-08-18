# your_app/ldap_utils.py

from ldap3 import Server, Connection, ALL, SIMPLE, SUBTREE
from ldap3.core.exceptions import LDAPException

def authenticate_and_get_user_info(login, password):
    LDAP_SERVER = 'ldap://dc001.apa.kz'
    LDAP_BASE_DN = 'dc=apa,dc=kz'
    SEARCH_FILTER = f'(userPrincipalName={login})'

    try:
        server = Server(LDAP_SERVER, get_info=ALL)
        conn = Connection(server, user=login, password=password, authentication=SIMPLE, auto_bind=True)

        conn.search(
            search_base=LDAP_BASE_DN,
            search_filter=SEARCH_FILTER,
            search_scope='SUBTREE',
            attributes=[
                'displayName',
                'mail',
                'telephoneNumber',
                'title',
                'department',
                'objectGUID'
            ]
        )

        if conn.entries:
            entry = conn.entries[0]
            return {
                'status': 'success',
                'displayName': entry['displayName'].value,
                'mail': entry['mail'].value,
                'telephoneNumber': entry['telephoneNumber'].value,
                'title': entry['title'].value,
                'department': entry['department'].value,
                'objectGUID': entry['objectGUID'].value.strip("{}").upper()
            }
        else:
            return {'status': 'failure', 'error': 'User not found'}

    except LDAPException as e:
        return {'status': 'failure', 'error': str(e)}
