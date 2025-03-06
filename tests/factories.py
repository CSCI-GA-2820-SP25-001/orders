"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Order, OrderItems


class OrderFactory(factory.Factory):
    """Creates fake orders"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Order

    id = factory.Sequence(lambda n: n)
    customer_id = factory.Sequence(lambda n: n)
    order_status = factory.Faker(
        "random_element", elements=("Received", "Shipped", "Delivered")
    )
    order_created = factory.Faker("date_time")
    order_updated = factory.Faker("date_time")

    @factory.post_generation
    def order_items(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the order items list"""
        if not create:
            return

        if extracted:
            self.order_items = extracted


class OrderItemsFactory(factory.Factory):
    """Creates fake order items"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = OrderItems

    id = factory.Sequence(lambda n: n)
    product_id = factory.Sequence(lambda n: n)
    quantity = factory.Sequence(lambda n: n)
    price = factory.Faker(
        "random_number",
        digits=2,
        fix_len=False,
        min=1.00,
        max=20.00,
    )
    order = factory.SubFactory(OrderFactory)
    order_id = factory.SelfAttribute("order.id")
