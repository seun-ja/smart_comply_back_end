class TransactionStatus:
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

    CHOICES = [
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
    ]


class TransactionType:
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"

    CHOICES = [
        (DEPOSIT, "Deposit"),
        (WITHDRAWAL, "Withdrawal"),
        (TRANSFER, "Transfer"),
    ]