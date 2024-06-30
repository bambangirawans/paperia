import xendit
from xendit import Xendit, Invoice

# Initialize Xendit API client
xendit.api_key = "YOUR_XENDIT_API_KEY"

def process_payment(data):
    try:
        # Extract necessary data from the request
        external_id = data.get('external_id')
        amount = data.get('amount')
        payer_email = data.get('payer_email')
        description = data.get('description')

        if not external_id or not amount or not payer_email or not description:
            return {'status': 'error', 'message': 'Missing required payment data'}

        # Create an invoice with Xendit
        invoice = Invoice.create(
            external_id=external_id,
            amount=amount,
            payer_email=payer_email,
            description=description,
        )

        return {
            'status': 'success',
            'message': 'Payment processed successfully',
            'invoice_url': invoice.invoice_url,
            'invoice_id': invoice.id
        }

    except xendit.XenditError as e:
        return {'status': 'error', 'message': str(e)}

