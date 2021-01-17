# custom classes for nylas

# connected: An Account has been connected to your app
# running: An Account is syncing and properly running
# stopped: An account was stopped or canceled
# invalid: an account has invalid credentials and needs to be reauthed
# sync_error: An account has a sync error and is no longer syncing
class NylasAccountStatus:
    def __init__(self, object):
        self.date_received = object["date"]  # date received the webhook it comes as epoch
        self.resource, self.resource_status = object["type"].split(".")
        self.details = object[
            "object_data"
        ]  # the meta data namespace_id, account_id, object attributes, id additional meta

    def __str__(self):

        return (
            f"{self.resource} with {self.details['account_id']} is currently {self.resource_status}"
        )

    def __dict__(self):
        return {
            "date_received": self.date_received,
            "resource": self.resource,
            "resource_status": self.resource_status,
            "details": self.details,
        }

    @property
    def data(self):
        """ returns an object as a dictionary to pass in response if needed """
        return self.__dict__()

    @property
    def account_id(self):
        """ helper to retrun account_id """
        return self.details["account_id"]


# from managr.core.nylas.models import NylasAccountStatus, NylasAccountStatusList


class NylasAccountStatusList:
    # TODO: Add __iter__ class to make iterable pb 09/30
    def __init__(self, deltas):

        self.items = [NylasAccountStatus(item) for item in deltas]

    def values(self, *args):
        """ returns values as list of lists for each key passed if it exists"""
        collected = []
        for v in self.items:
            current = []
            for key in args:
                val = v.data.get(key, None)
                if val:
                    current.append(val)
                collected.append(current)
        return collected
