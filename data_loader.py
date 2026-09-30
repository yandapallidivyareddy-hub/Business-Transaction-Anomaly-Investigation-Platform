from nova_client import nova_get, list_all


def get_payments():
    return list_all("/payments")


def get_invoices():
    return list_all("/invoices")


def get_vendors():
    return list_all("/vendors")


def get_vendor_payments():
    return list_all("/vendor-payments")


def get_bank_transactions():
    return list_all("/bank-transactions")


def get_approvals():
    return list_all("/approvals")


def get_master_data_changes():
    return list_all("/master-data-changes")