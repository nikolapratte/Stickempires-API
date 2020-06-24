"""Pytest tests"""
# TODO move tests to a testing folder

from helpers import CounterLE



def test_smaller():
    a = CounterLE("575")
    b = CounterLE("575124")

    assert a <= b


def test_missing():
    a = CounterLE("575")
    b = CounterLE("124")

    assert not (a <= b)


def test_multiple():
    a = CounterLE("575")
    b = CounterLE("57124")

    assert not (a <= b)


def test_multiple2():
    a = CounterLE("575")
    b = CounterLE("55124")

    assert not (a <= b)


def test_zero():
    a = CounterLE("0")
    b = CounterLE("124")

    assert not (a <= b)


def test_bigger():
    a = CounterLE("5755")
    b = CounterLE("575")

    assert not (a <= b)