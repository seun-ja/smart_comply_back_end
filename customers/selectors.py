from .models import Customer


class CustomerService:
    @staticmethod
    def create(data):
        data.pop("is_high_risk", None)

        return Customer.objects.create(**data)

    @staticmethod
    def update(customer, data):
        data.pop("is_high_risk", None)

        for key, value in data.items():
            setattr(customer, key, value)

        customer.save()

        return customer
