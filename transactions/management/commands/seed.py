import random
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from customers.models import Customer
from transactions.models import (
    TransactionStatus,
    TransactionType,
)
from transactions.services import TransactionService

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with sample data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--transactions",
            type=int,
            default=100,
            help="Number of transactions to generate",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🌱 Seeding database..."))

        self.create_admin()
        customers = self.create_customers()
        count = options["transactions"]
        self.create_transactions(customers, count)

        self.stdout.write(self.style.SUCCESS("✅ Database seeded successfully."))

    def create_admin(self):
        if User.objects.filter(username="admin").exists():
            return

        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123",
        )

        self.stdout.write("Created admin user")

    def create_customers(self):
        customers = []

        data = [
            ("Joshua", "Aminu", "joshua@example.com", "NG"),
            ("John", "Doe", "john@example.com", "US"),
            ("Jane", "Smith", "jane@example.com", "GB"),
            ("Alice", "Brown", "alice@example.com", "CA"),
            ("David", "Wilson", "david@example.com", "ZA"),
            ("Fatima", "Ahmed", "fatima@example.com", "AE"),
            ("Michael", "Johnson", "michael@example.com", "FR"),
            ("Grace", "Okafor", "grace@example.com", "NG"),
            ("Daniel", "Lee", "daniel@example.com", "SG"),
            ("Sarah", "Kim", "sarah@example.com", "KR"),
        ]

        for first, last, email, country in data:
            customer, _ = Customer.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "country": country,
                },
            )

            customers.append(customer)

        self.stdout.write(f"Created {len(customers)} customers")

        return customers

    def create_transactions(self, customers, count):
        currencies = ["USD", "EUR", "GBP", "NGN"]
        types = [
            TransactionType.DEPOSIT,
            TransactionType.WITHDRAWAL,
            TransactionType.TRANSFER,
        ]

        for _ in range(count):
            customer = random.choice(customers)

            TransactionService.create(
                {
                    "customer": customer,
                    "amount": Decimal(random.randint(50, 20000)),
                    "currency": random.choice(currencies),
                    "transaction_type": random.choice(types),
                    "status": TransactionStatus.PENDING,
                }
            )

        self.stdout.write(f"Created {count} transactions")
