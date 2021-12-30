from collections import Mapping
import jmespath

import common
from repository import Repository
import vanity_number


def handler(event, context):

    vanity_numbers = []
    result = 'Unable to generate vanity numbers. Please contact administrator.'
    customer = jmespath.search('Details.ContactData.CustomerEndpoint', event)
    common.info('Processing contact %s' % str(customer))
    if isinstance(customer, Mapping):
        contact_type = customer.get('Type')
        if contact_type == 'TELEPHONE_NUMBER':
            phone_number = customer.get('Address')
            contact_repository = Repository('contacts_store', 'phoneNumber')
            contact = contact_repository.exists(phone_number)
            if isinstance(contact, Mapping):
                common.info('Contact exists: %s' % phone_number)
                vanity_numbers = contact.get('vanityNumbers')
                contact_repository.write(phone_number, vals={
                    'vanityNumbers': vanity_numbers
                }, update=True)
            else:
                common.info('Creating new contact: %s' % phone_number)
                vanity_numbers = vanity_number.generate(phone_number)
                contact_repository.write(phone_number, vals={
                    'vanityNumbers': vanity_numbers
                })
        else:
            result = 'Unsupported customer type'
    else:
        result = 'Invalid event'
    if len(vanity_numbers) > 0:
        result = ',  '.join(vanity_numbers)
        result = 'Here are your %s vanity numbers: %s' % (len(vanity_numbers), result)
    common.info('Processed contact: %s; result: %s' % (phone_number, result))
    return {
        "result": result
    }
