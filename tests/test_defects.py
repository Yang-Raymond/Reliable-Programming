"""Unit tests for the defects listed in DEFECTS.md."""
import pytest

from setup_db import initialize
from repository import StoreRepository
from cart import ShoppingCart
from checkout import CheckoutService
from payments import FakePaymentGateway
from models import CartLine


@pytest.fixture
def repo(tmp_path):
    db = str(tmp_path / 'test.db')
    initialize(db)
    return StoreRepository(db)


# Defect 1: inventory only changes after a successful payment
def test_declined_payment_does_not_reduce_stock(repo):
    cart = ShoppingCart('u1', repo)
    cart.add_item('MOU-01', 2)
    result = CheckoutService(repo, FakePaymentGateway(should_approve=False)).checkout(cart, 'tok', 'r1')
    assert result.status == 'declined'
    assert repo.get_product('MOU-01').stock == 20


def test_paid_checkout_reduces_stock(repo):
    cart = ShoppingCart('u1', repo)
    cart.add_item('MOU-01', 2)
    result = CheckoutService(repo, FakePaymentGateway()).checkout(cart, 'tok', 'r1')
    assert result.status == 'paid'
    assert repo.get_product('MOU-01').stock == 18


# Defect 2: SAVE15 doesn't apply to carts under $15
def test_save15_rejected_under_15(repo):
    cart = ShoppingCart('u1', repo)
    cart.add_item('USB-01', 1)
    assert cart.apply_discount('SAVE15') is False
    assert cart.total() == pytest.approx(9.99)


def test_save15_applies_at_or_above_15(repo):
    cart = ShoppingCart('u1', repo)
    cart.add_item('MOU-01', 1)
    assert cart.apply_discount('SAVE15') is True
    assert cart.total() == pytest.approx(14.95)


# Defect 3: get_saved_cart SQL injection attack
def test_get_saved_cart_injection_returns_nothing(repo):
    repo.save_cart('alice', [CartLine('USB-01', 'USB cable', 9.99, 2)])
    assert repo.get_saved_cart("x' OR '1'='1") == []


def test_get_saved_cart_returns_only_own_items(repo):
    repo.save_cart('alice', [CartLine('USB-01', 'USB cable', 9.99, 2)])
    repo.save_cart('bob', [CartLine('MOU-01', 'Wireless mouse', 29.95, 1)])
    assert repo.get_saved_cart('alice') == [('USB-01', 2)]


# Defect 4: get_product SQL injection attack
def test_get_product_injection_returns_none(repo):
    assert repo.get_product("x' OR '1'='1") is None


# Defect 5: list_orders only returns the given user's orders
def test_list_orders_only_returns_users_orders(repo):
    repo.save_order('a', 10.0, 'paid', 'r1')
    repo.save_order('b', 20.0, 'paid', 'r2')
    orders = repo.list_orders('a')
    assert len(orders) == 1
    assert all(row[1] == 'a' for row in orders)


# Defect 6: add_item rejects if quantity is negative or zero
def test_add_item_rejects_negative_quantity(repo):
    cart = ShoppingCart('u1', repo)
    assert cart.add_item('USB-01', -3) is False
    assert cart.lines == []


def test_add_item_rejects_zero_quantity(repo):
    cart = ShoppingCart('u1', repo)
    assert cart.add_item('USB-01', 0) is False
    assert cart.lines == []


# Defect 7: remove_item rejects if quantity is negative or zero
def test_remove_item_rejects_negative_quantity(repo):
    cart = ShoppingCart('u1', repo)
    cart.add_item('USB-01', 2)
    assert cart.remove_item('USB-01', -5) is False
    assert cart.lines[0].quantity == 2


# Defect 8: discounts are calculated from the subtotal
def test_discounts_do_not_stack(repo):
    cart = ShoppingCart('u1', repo)
    cart.add_item('USB-01', 10)
    cart.apply_discount('STUDENT20')
    cart.apply_discount('STUDENT20')
    assert cart.total() == pytest.approx(79.92)
