from django.utils import timezone
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from datetime import timedelta
#from smart_apa_api.models import User
from smart_apa_api.models import SmartApaUser
from smart_apa_api.ldap_utils import authenticate_and_get_user_info  # Import your function


class DummyUser:
    def __init__(self, username):
        self.username = username
        self.id = 9999  # some constant ID
        self.is_active = True

def authenticate1(login, password):
    try:

        email_list = [
            "d.bolatbek@apa.kz",
            "alua.makhat@apa.kz",
            "m.mukataev@apa.kz",
            "s.ualbekov@apa.kz",
            "k.kulynchakov@apa.kz",
            "a.kerimbayev@apa.kz",
            "test@apa.kz"
        ]
        
        if login not in email_list:
            return None

        user = SmartApaUser.objects.get(login=login)
    except SmartApaUser.DoesNotExist:
        # Try LDAP/AD fallback
        result = authenticate_and_get_user_info(login, password)
        if result['status'] != 'success':
            return None  # Not found anywhere
        
        # Create user in DB
        user = SmartApaUser.objects.create(
            login=login,
            password_hash=make_password(password),
            display_name=result['displayName'],
            title=result['title'],
            department=result['department'],
            last_ad_check=timezone.now(),
            is_active=True,
        )
        user.object_guid=result['objectGUID'] 
        return user

    # Inactive user
    if not user.is_active:
        return None  # User is deactivated
        
    now = timezone.now()

    # Blocked user
    if user.blocked_until and user.blocked_until > now:
        return None  # Still blocked

    # Check password
    if not check_password(password, user.password_hash):
        user.bad_pwd_count += 1

        # Block user after 100 failed attempts
        if user.bad_pwd_count >= 100:
            user.blocked_until = now + timedelta(minutes=3)

        user.save()
        return None

    # Success: 
    if user.last_ad_check and user.last_ad_check + timedelta(minutes=3) < now:
        # Try LDAP/AD fallback
        result = authenticate_and_get_user_info(login, password)
        # Block user
        if result['status'] != 'success':
            user.is_active = False
            user.save()
            return None

        # Update user data from LDAP/AD
        user.display_name=result['displayName']
        user.title=result['title']
        user.department=result['department']
        user.last_ad_check=timezone.now()
        user.object_guid=result['objectGUID']

    # Reset counters
    user.bad_pwd_count = 0
    user.blocked_until = None

    user.last_login = timezone.now()

    user.save()

    return user


def authenticate2(login, password):
    try:
        user = SmartApaUser.objects.get(login=login)
    except SmartApaUser.DoesNotExist:
        # Try LDAP/AD fallback
        result = authenticate_and_get_user_info(login, password)
        if result['status'] != 'success':
            return None  # Not found anywhere
        
        # Create user in DB
        user = SmartApaUser.objects.create(
            login=login,
            password_hash=make_password(password),
            display_name=result['displayName'],
            title=result['title'],
            department=result['department'],
            last_ad_check=timezone.now(),
            is_active=True,
        )
        return user

    # Inactive user
    if not user.is_active:
        return None  # User is deactivated
        
    now = timezone.now()

    # Blocked user
    if user.blocked_until and user.blocked_until > now:
        return None  # Still blocked

    # Check password
    if not check_password(password, user.password_hash):
        user.bad_pwd_count += 1

        # Block user after 3 failed attempts
        if user.bad_pwd_count >= 3:
            user.blocked_until = now + timedelta(minutes=30)

        user.save()
        return None

    # Success: 
    if user.last_ad_check and user.last_ad_check + timedelta(minutes=60) < now:
        # Try LDAP/AD fallback
        result = authenticate_and_get_user_info(login, password)
        # Block user
        if result['status'] != 'success':
            user.is_active = False
            user.save()
            return None

        # Update user data from LDAP/AD
        user.display_name=result['displayName']
        user.title=result['title']
        user.department=result['department']
        user.last_ad_check=timezone.now()

    # Reset counters
    user.bad_pwd_count = 0
    user.blocked_until = None
    
    user.save()

    return user


def authenticate3(login, password):
    try:
        email_list = [
            "d.bolatbek@apa.kz",
            "alua.makhat@apa.kz",
            "m.mukataev@apa.kz",
            "s.ualbekov@apa.kz",
            "k.kulynchakov@apa.kz",
            "a.kerimbayev@apa.kz",
            "j.depp@apa.kz"
        ]
        
        if login not in email_list:
            return None
            
        user = SmartApaUser.objects.get(login=login)
    except SmartApaUser.DoesNotExist:
        # Try LDAP/AD fallback
        result = authenticate_and_get_user_info(login, password)
        if result['status'] != 'success':
            return None  # Not found anywhere
        
        # Create user in DB
        user = SmartApaUser.objects.create(
            login=login,
            password_hash=make_password(password),
            display_name=result['displayName'],
            title=result['title'],
            department=result['department'],
            last_ad_check=timezone.now(),
            is_active=True,
        )
        return user

    # Inactive user
    if not user.is_active:
        return None  # User is deactivated
        
    now = timezone.now()

    # Blocked user
    if user.blocked_until and user.blocked_until > now:
        return None  # Still blocked

    # Check password
    if not check_password(password, user.password_hash):
        user.bad_pwd_count += 1

        # Block user after 3 failed attempts
        if user.bad_pwd_count >= 3:
            user.blocked_until = now + timedelta(minutes=30)

        user.save()
        return None

    # Success: 
    if user.last_ad_check and user.last_ad_check + timedelta(minutes=60) < now:
        # Try LDAP/AD fallback
        result = authenticate_and_get_user_info(login, password)
        # Block user
        if result['status'] != 'success':
            user.is_active = False
            user.save()
            return None

        # Update user data from LDAP/AD
        user.display_name=result['displayName']
        user.title=result['title']
        user.department=result['department']
        user.last_ad_check=timezone.now()

    # Reset counters
    user.bad_pwd_count = 0
    user.blocked_until = None
    
    user.last_login = timezone.now()

    user.save()



    return user    