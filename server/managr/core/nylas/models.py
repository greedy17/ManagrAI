# custom classes for nylas


class NylasAccountStatus:
    def __init__(self, date, object, type, object_data):
        self.date_received = date  # date received the webhook it comes as epoch
        self.resource = object  # the resource being targeted (account, message)
        self.resource_status = type  # the webhook trigger object.status account.running
        self.details = object_data  # the meta data namespace_id, account_id, object attributes, id additional meta

    def __str__(self):
        resource, status = self.resource_status.split(".")
        return f"{resource} with {self.details.account_id} is currently {status}"

    def __dict__(self):
        return {
            "date_received": self.date_received,
            "resource": self.resource,
            "resource_status": self.resource_status,
            "details": self.object_data,
        }

    @property
    def data(self):
        """ returns an object as a dictionary to pass in response if needed """
        return self.__data__()


class NylasAccountStatusList:
    def __init__(self, deltas):
        self.items = [NylasAccountStatus(item) for item in deltas]

    def __iter__(self):
        for item in self.items:
            yield item

