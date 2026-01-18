from users.models import Transaction

def create_transaction(user, travels, amount, transaction_type, description=None):
    """
    Creates a transaction and updates the profile's coin balance
    """
    if transaction_type not in [choice[0] for choice in Transaction.TRANSACTION_TYPES]:
        raise ValueError("Invalid transaction type")
    
    # Create the transaction record
    transaction = Transaction.objects.create(
        user=user,
        travels=travels,
        amount=amount,
        transaction_type=transaction_type,
        description=description
    )
    
    # Update the profile's coin balance
    if transaction_type == 'BOOKING':
        if user.profile.coins < amount:
            raise ValueError("Insufficient coins")
        user.profile.coins -= amount
        travels.profile.coins += amount


    elif transaction_type == 'CANCELLATION':
        user.profile.coins += amount
        travels.profile.coins -= amount
    
    elif transaction_type == 'ADD_COINS':
        user.profile.coins += amount
    
    user.profile.save()
    if travels:
        travels.profile.save()

    return transaction