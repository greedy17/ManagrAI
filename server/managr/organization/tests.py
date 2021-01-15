import copy
import json
from django.test import TestCase
from django.urls import reverse
from faker import Faker
from django.test import RequestFactory
from django.test import Client

from rest_framework.authtoken.models import Token
from rest_framework import status

