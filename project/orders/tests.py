import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from .models import Product, Order
from django.contrib.auth.models import User
from rest_framework import status


@pytest.fixture
def api_client():
    # Returns a new API client instance for testing
    return APIClient()


@pytest.fixture
def user(db):
    # Creates a new user in the database with a given username and password
    return User.objects.create_user(username='testuser', password='testpass')


@pytest.fixture
def products():
    # Creates a product instance (shampoo) and returns it in a list
    product1 = Product.objects.create(name='shampoo', price=50, quantity=1)
    return [product1]


@pytest.mark.django_db
def test_create_order(api_client, user, products):
    # Force the API client to authenticate as the test user
    api_client.force_authenticate(user=user)

    # Define the order data to be sent in the request
    url = reverse('order-list')
    data = {
        "user": user.id,  # Pass the user ID
        "status": "pending",
        "total_price": "450.00",
        "products": [
            {"name": "shampoo", "price": "35.00", "quantity": 1}
        ]
    }

    # Send POST request to create the order
    response = api_client.post(url, data, format='json')

    # Assert that the order creation was successful (status code 201)
    assert response.status_code == status.HTTP_201_CREATED
    assert Order.objects.count() == 1  # Ensure one order has been created
    order = Order.objects.first()
    assert order.user == user  # Ensure the user is correctly assigned to the order


@pytest.mark.django_db
def test_list_orders(api_client, user, products):
    # Force the API client to authenticate as the test user
    api_client.force_authenticate(user=user)

    # Create an order via API request
    url = reverse('order-list')
    data = {
        "user": user.id,  # Pass the user ID
        "status": "pending",
        "total_price": "400.00",
        "products": [
            {"name": "shampoo", "price": "40.00", "quantity": 1}
        ]
    }

    # Send POST request to create the order
    response = api_client.post(url, data, format='json')

    # Assert that the order was created successfully
    assert response.status_code == status.HTTP_201_CREATED

    # Request the list of orders
    response = api_client.get(url)

    # Assert that the request was successful and the list contains the created order
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['user'] == user.username  # Ensure the user is correctly assigned


@pytest.mark.django_db
def test_update_order(api_client, user, products):
    # Force the API client to authenticate as the test user
    api_client.force_authenticate(user=user)

    # Create an order and assign products to it
    order = Order.objects.create(
        user=user,  # Use the user object
        status='pending',
        total_price='40.00',
    )
    order.products.set(products)

    # Define the URL and the updated data
    url = reverse('order-detail', args=[order.order_id])
    data = {
        "user": user.id,  # Pass the user ID
        "status": "confirmed",  # Change status to "confirmed"
        "total_price": "50.00",  # Update the price
        "products": [
            {"name": "shampoo", "price": "50.00", "quantity": 2}
        ]
    }

    # Send PUT request to update the order
    response = api_client.put(url, data, format='json')

    # Assert that the order was updated successfully (status code 200)
    assert response.status_code == status.HTTP_200_OK
    order.refresh_from_db()  # Refresh the order from the database
    assert order.user == user  # Ensure the user remains the same
    assert order.status == 'confirmed'  # Ensure the status was updated


@pytest.mark.django_db
def test_delete_order(api_client, user, products):
    # Force the API client to authenticate as the test user
    api_client.force_authenticate(user=user)

    # Create an order and assign products to it
    order = Order.objects.create(
        user=user,
        status='pending',
        total_price='40.00',
    )
    order.products.set(products)

    # Define the URL for deleting the order
    url = reverse('order-detail', args=[order.order_id])
    response = api_client.delete(url)

    # Assert that the deletion request was successful (status code 200)
    assert response.status_code == status.HTTP_200_OK

    # Refresh the order from the database and check if it's marked as deleted
    order.refresh_from_db()
    assert order.is_deleted is True  # Ensure the is_deleted flag is set to True

    # Ensure the order is still in the database, but marked as deleted
    assert Order.objects.count() == 1


@pytest.mark.django_db
def test_metrics(api_client, user, products):
    # Force the API client to authenticate as the test user
    api_client.force_authenticate(user=user)

    # Get metrics before making any requests
    metrics_before = api_client.get(reverse('metrics'))
    assert metrics_before.status_code == status.HTTP_200_OK
    metrics_before_data = metrics_before.json()

    # Make a valid order creation request
    url = reverse('order-list')
    data = {
        "user": user.id,
        "status": "pending",
        "total_price": "40.00",
        "products": [
            {"name": "shampoo", "price": "60.00", "quantity": 1}
        ]
    }
    response = api_client.post(url, data, format='json')

    # Assert the order was successfully created
    assert response.status_code == status.HTTP_201_CREATED

    # Get metrics after successful request
    metrics_after_success = api_client.get(reverse('metrics'))
    assert metrics_after_success.status_code == status.HTTP_200_OK
    metrics_after_success_data = metrics_after_success.json()

    # Ensure metrics have been updated with the successful request
    assert metrics_after_success_data != metrics_before_data  # Metrics should have changed
    assert metrics_after_success_data['/api/v1/orders/']['total_calls'] == metrics_before_data['/api/v1/orders/']['total_calls'] + 1
    assert metrics_after_success_data['/api/v1/orders/']['success'] == metrics_before_data['/api/v1/orders/']['success'] + 1

    # Make an invalid order creation request (missing user)
    invalid_data = {
        "status": "pending",  # Missing user (required)
        "total_price": "40.00",
        "products": [
            {"name": "shampoo", "price": "70.00", "quantity": -1}  # Invalid quantity (negative)
        ]
    }
    response_invalid = api_client.post(url, invalid_data, format='json')

    # Assert that the request failed (status code 400)
    assert response_invalid.status_code == status.HTTP_400_BAD_REQUEST

    # Get metrics after the failed request
    metrics_after_error = api_client.get(reverse('metrics'))
    assert metrics_after_error.status_code == status.HTTP_200_OK
    metrics_after_error_data = metrics_after_error.json()

    # Ensure metrics have been updated with the failed request (error count should increase)
    assert metrics_after_error_data != metrics_after_success_data  # Metrics should have changed
    assert metrics_after_error_data['/api/v1/orders/']['total_calls'] == metrics_after_success_data['/api/v1/orders/']['total_calls'] + 1
    assert metrics_after_error_data['/api/v1/orders/']['errors'] == metrics_after_success_data['/api/v1/orders/']['errors'] + 1


@pytest.mark.django_db
def test_filter_orders_by_status(api_client, user, products):
    # Authenticate the user for the API request
    api_client.force_authenticate(user=user)

    # Create multiple orders with different statuses
    Order.objects.create(
        user=user,
        status='pending',
        total_price='40.00',
    )
    Order.objects.create(
        user=user,
        status='confirmed',
        total_price='50.00',
    )

    # Create URL with the filter for the status
    url = reverse('order-list') + '?status=pending'

    # Perform the GET request with the filter
    response = api_client.get(url)

    # Check that filtering works and only one order with the correct status is returned
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['status'] == 'pending'


@pytest.mark.django_db
def test_filter_orders_by_price_range(api_client, user, products):
    # Authenticate the user for the API request
    api_client.force_authenticate(user=user)

    # Create orders with different total prices
    Order.objects.create(
        user=user,
        status='pending',
        total_price='30.00',
    )
    Order.objects.create(
        user=user,
        status='confirmed',
        total_price='50.00',
    )
    Order.objects.create(
        user=user,
        status='pending',
        total_price='70.00',
    )

    # Test filtering by minimum price
    url_min = reverse('order-list') + '?min_price=40.00'
    response_min = api_client.get(url_min)
    # Check that the response contains only orders with price >= 40.00
    assert response_min.status_code == status.HTTP_200_OK
    assert len(response_min.data) == 2  # There should be two orders with price >= 40.00

    # Test filtering by maximum price
    url_max = reverse('order-list') + '?max_price=50.00'
    response_max = api_client.get(url_max)
    # Check that the response contains only orders with price <= 50.00
    assert response_max.status_code == status.HTTP_200_OK
    assert len(response_max.data) == 2  # There should be two orders with price <= 50.00

    # Test filtering by price range (min_price and max_price)
    url_range = reverse('order-list') + '?min_price=40.00&max_price=60.00'
    response_range = api_client.get(url_range)
    # Check that the response contains only orders within the price range 40.00 to 60.00
    assert response_range.status_code == status.HTTP_200_OK
    assert len(response_range.data) == 1  # There should be one order with price in the range 40.00 to 60.00
