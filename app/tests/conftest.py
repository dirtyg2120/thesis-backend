# import pytest
from mongoengine import connect, disconnect
        
def pytest_configure():
    print("--------------STARTED------------")
    connect('mongoenginetest', host='mongomock://localhost')

def pytest_sessionfinish(session, exitstatus):
    print('--------------ENDED-------------------')
    disconnect()