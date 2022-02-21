from os import remove
from posixpath import split
from xml.etree import cElementTree as ElementTree
from django.db.models import Q

SALESFORCE_BODY_TAG = "{http://schemas.xmlsoap.org/soap/envelope/}Body"
SALESFORCE_FAULT_TAG = "{http://schemas.xmlsoap.org/soap/envelope/}Fault"
SALESFORCE_INNER_TAG = "{urn:partner.soap.sforce.com}"
SALESFORCE_SUCCESS_TAG = "{urn:partner.soap.sforce.com}convertLeadResponse"
SALESFORCE_RESULT_TAG = "{urn:partner.soap.sforce.com}result"
SALESFORCE_BOOLEAN_TAG = "{http://www.w3.org/2001/XMLSchema-instance}nil"


class XmlListConfig(list):
    def __init__(self, aList):
        for element in aList:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)


class XmlDictConfig(dict):
    """
    Example usage:

    >>> tree = ElementTree.parse('your_file.xml')
    >>> root = tree.getroot()
    >>> xmldict = XmlDictConfig(root)

    Or, if you want to use an XML string:

    >>> root = ElementTree.XML(xml_string)
    >>> xmldict = XmlDictConfig(root)

    And then use xmldict for what it is... a dict.
    """

    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself
                    aDict = {element[0].tag: XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})


def remove_tags(dictionary, custom_tag=None, previous_key=None):
    cleaned_object = {}
    for key in list(dictionary.keys()):
        if SALESFORCE_INNER_TAG in key:
            new_key = key.replace(SALESFORCE_INNER_TAG, "")
        elif SALESFORCE_BOOLEAN_TAG in key:
            return dictionary[key]
        else:
            new_key = key.replace(custom_tag, "")
        if isinstance(dictionary[key], dict):
            cleaned_object[new_key] = remove_tags(dictionary[key], previous_key=new_key)
        else:
            cleaned_object[new_key] = dictionary[key]
    return cleaned_object


def process_xml_dict(xml_response):
    convert = ElementTree.XML(xml_response)
    xmldict = XmlDictConfig(convert)
    processed_dict = dict()
    body = xmldict[SALESFORCE_BODY_TAG]
    if SALESFORCE_FAULT_TAG in body:
        processed_dict["error_data"] = body[SALESFORCE_FAULT_TAG]
    else:
        body_keys = list(body.keys())
        success_key = body_keys[0].replace(SALESFORCE_INNER_TAG, "")
        result_key = list(body[SALESFORCE_SUCCESS_TAG].keys())[0].replace(SALESFORCE_INNER_TAG, "")
        result_dict = remove_tags(body[SALESFORCE_SUCCESS_TAG][SALESFORCE_RESULT_TAG])
        processed_dict[success_key] = {result_key: result_dict}
    return processed_dict


def process_text_field_format(user_id, resource, saved_data):
    from managr.core.models import User
    from managr.salesforce.models import SObjectField

    user = User.objects.get(id=user_id)
    fields = list(
        SObjectField.objects.for_user(user)
        .filter(Q(salesforce_object=resource, data_type="TextArea"))
        .values_list("api_name", flat=True)
    )
    to_check_fields = [field for field in saved_data if field in fields]
    if len(to_check_fields):
        for field in to_check_fields:
            if saved_data[field]:
                split_field = saved_data[field].split("\n")
                if len(split_field) > 1:
                    salesforce_formatted = "\r\n".join(split_field)
                    saved_data[field] = salesforce_formatted
        return saved_data
    return False
