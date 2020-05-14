import kronos
import requests
from managr.core.integrations import revoke_all_access_tokens
from managr.core.models import User, EmailAuthAccount


# Daily, at hour 0, minute 0 (12am)
@kronos.register('0 0 * * *')
def revoke_extra_access_tokens():
    """ this will remove excess access tokens 
        managr will be charged for excess tokens as accounts
        it will only keep access tokens we have stored in the
        EmailAuthAccount regardless of sync status
    """
    for row in EmailAuthAccount.objects.all():
        print('tokens removed')
        try:
            revoke_all_access_tokens(
                row.account_id, keep_token=row.access_token)
            row.delete()

        except requests.exceptions.HTTPError as e:
            if 404 in e.args:
                # delete the record so we can create a new link
                row.email_auth_account.delete()
                # we have out of sync data, pass
                # we have a cron job running every 24 hours to remove all old tokens which are not in sync
                pass
            else:
                """ most likely an error with our account or their server will just log this when the logger is set up"""
                continue
