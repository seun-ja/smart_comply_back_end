from .models import Transaction


class TransactionSelector:
    @staticmethod
    def all():

        return Transaction.objects.select_related("customer").all()

    @staticmethod
    def by_reference(reference):

        return Transaction.objects.select_related("customer").get(reference=reference)

    @staticmethod
    def by_id(pk):

        return Transaction.objects.select_related("customer").get(pk=pk)


def transaction_detail(pk):
    return (
        Transaction.objects.select_related("customer")
        .prefetch_related("alerts", "audit_logs")
        .get(pk=pk)
    )
