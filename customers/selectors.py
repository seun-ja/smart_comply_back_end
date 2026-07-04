from .models import Customer


class CustomerService:

    @staticmethod
    def create(data):

        return Customer.objects.create(**data)

    @staticmethod
    def update(customer, data):

        for key, value in data.items():
            setattr(customer, key, value)

        customer.save()

        return customer