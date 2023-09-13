import re
import boto3
from cryptography.fernet import Fernet
from django.conf import settings
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import filters
from django.core.paginator import Paginator
import base64
import hashlib


def to_snake_case(val):
    # note if first value is capital then it will return a starting _
    if not val:
        return
    value = str(val)
    for index, char in enumerate(re.finditer(r"[A-Z]", value)):
        if char.start() == 0:
            value = value.lower()
        else:
            value = (
                value[: index + char.start()]
                + "_"
                + value[index + char.start()].lower()
                + value[index + char.start() + 1 :]
            )
    return value


def phrase_to_snake_case(val):
    if not val:
        return
    value = str(val)
    value = value.replace(" ", "_").lower()
    return value


def object_to_snake_case(obj):
    if type(obj) != dict and type(obj) != str:
        return obj
    elif type(obj) == str:
        return to_snake_case(obj)
    new_obj = dict()
    for k, v in obj.items():
        if type(v) == list:
            new_obj[to_snake_case(k)] = []
            for item in v:
                if type(item) == dict:
                    new_obj[to_snake_case(k)].append(object_to_snake_case(item))
                else:
                    new_obj[to_snake_case(k)].append(item)

            list(map(lambda new_v: object_to_snake_case(new_v) if type(new_v) == dict else v, v))
        elif type(v) == dict:
            new_obj[to_snake_case(k)] = object_to_snake_case(v)
        else:
            new_obj[to_snake_case(k)] = v
    return new_obj


def snake_to_space(word):
    _matches = []
    if type(word) != str:
        return word
    if not len(word):
        return word
    while True:
        matches = re.search(r"_", word)
        if matches:
            _matches.append(matches.end())
            word = re.sub("_", " ", word, 1)

        else:
            break

    for match in _matches:
        word = word[0].upper() + word[1:match] + word[match].upper() + word[match + 1 :]

    if not len(_matches):
        word = word[0].upper() + word[1:]
    return word


def datetime_appended_filepath(instance, filename):
    """
    Appending datetime to filepath makes each filepath unique.
    This prevents users from overwriting each others' files.
    """
    extension = filename.split(".")[-1]
    original_name = filename.split(".")[:-1][0]
    time = str(timezone.now().isoformat())
    time = time.split(".")[0]  # Remove trailing tz info
    name = f"{original_name}_{time}.{extension}"
    return name


def bucket_upload_filepath(organization_name, first_name, filename):
    extension = filename.split(".")[-1]
    original_name = filename.split(".")[:-1][0]
    time = str(timezone.now().isoformat())
    time = time.split(".")[0]  # Remove trailing tz info
    name = f"{organization_name}/{first_name}/{original_name}_{time}.{extension}"
    return name


def apply_filter_and_search(viewset, request):
    """
    Apply filter parameters and search query to a detailed endpoint.
    """
    # Get appropriate results from queryset method
    results = viewset.get_queryset()

    # Instantiate filter class to apply all query params as filters
    filter_set = viewset.filter_class(request=request, data=request.query_params)
    if filter_set.is_valid():
        results = filter_set.filter_queryset(results)

    # Apply 'search' filter to results as well, and return
    filter = filters.SearchFilter()
    return filter.filter_queryset(request, results, viewset)


def custom_paginator(items, serializer=None, count=7, page=1):
    paginator = Paginator(items, count)
    page = paginator.page(page)
    results = page.object_list
    next_page = page.next_page_number() if page.has_next() else None
    previous_page = page.previous_page_number() if page.has_previous() else None
    page_index = page.__str__()

    if serializer:
        results = serializer(results, many=True).data

    return {
        "count": paginator.count,
        "next_page": next_page,
        "previous_page": previous_page,
        "results": results,
        "page": page_index,
    }


def paginate_results(viewset, results, serializer, request=None):
    """
    Paginate results of a detail endpoint, which doesn't automatically
    respect default pagination settings.
    """
    page = viewset.paginate_queryset(results)

    if page is not None:
        serializer = serializer(page, many=True, context={"request": request})
        return viewset.get_paginated_response(serializer.data)

    serializer = serializer(results, many=True, context={"request": request})
    return Response(serializer.data, status=status.HTTP_200_OK)


def get_site_url():
    """Get the full base URL for this site based on settings."""
    protocol = "http" if settings.IN_DEV else "https"
    domain = settings.CURRENT_DOMAIN
    return "{0}://{1}{2}".format(
        protocol,
        domain,
        f":{settings.CURRENT_PORT}" if settings.CURRENT_PORT and settings.IN_DEV else "",
    )


def query_debugger(func):
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        reset_queries()

        start_queries = len(connection.queries)

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        end_queries = len(connection.queries)

        print(f"Function : {func.__name__}")
        print(f"Number of Queries : {end_queries - start_queries}")
        print(f"Finished in : {(end - start):.2f}s")
        return result

    return inner_func


def upload_to_bucket(file, filename, bucket_name, access_key_id, secret):
    AWS_ACCESS_KEY_ID = access_key_id
    AWS_SECRET_ACCESS_KEY = secret
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    s3.upload_file(file, bucket_name, filename)


def generate_fernet_key(secret_key):
    # Use a hash function to generate a 256-bit (32-byte) key
    key = hashlib.sha256(secret_key.encode()).digest()
    return base64.urlsafe_b64encode(key)


def encrypt_dict(data_dict):
    """
    Encrypts a dictionary using Fernet encryption.
    :param data_dict: Dictionary to be encrypted
    :return: Encrypted data as string
    """
    secret_key = settings.SECRET_KEY
    fernet_key = generate_fernet_key(secret_key)
    cipher_suite = Fernet(fernet_key)
    data_str = str(data_dict).encode("utf-8")
    encrypted_data = cipher_suite.encrypt(data_str)
    return encrypted_data.decode("utf-8")


def decrypt_dict(encrypted_data):
    """
    Decrypts Fernet-encrypted data and returns the original dictionary.
    :param encrypted_data: Encrypted data as string
    :return: Decrypted dictionary
    """
    encrypted_data = encrypted_data.encode("utf-8")
    secret_key = settings.SECRET_KEY
    fernet_key = generate_fernet_key(secret_key)
    cipher_suite = Fernet(fernet_key)
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    data_str = decrypted_data.decode("utf-8")
    decrypted_dict = eval(data_str)
    return decrypted_dict
