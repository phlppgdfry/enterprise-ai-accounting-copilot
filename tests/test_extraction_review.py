from accounting_copilot.extraction import review_fields, REQUIRED


def test_missing_and_uncalibrated_confidence_require_review():
    result = review_fields({'VendorName': {'valueString': 'Synthetic supplier', 'confidence': .98},
                            'InvoiceId': {'content': 'SYN-001', 'confidence': .4},
                            'InvoiceTotal': {'valueCurrency': {'amount': 121, 'currencyCode': 'EUR'}, 'confidence': float('nan')}})
    assert result['missing_fields'] == ['InvoiceDate', 'SubTotal', 'TotalTax']
    assert 'InvoiceId' in result['review_fields'] and 'InvoiceTotal' in result['review_fields']
    assert result['fields'][-1]['provider_confidence'] is None
    assert result['requires_human_review'] is True


def test_high_confidence_never_approves():
    result = review_fields({name: {'content': 'synthetic', 'confidence': 1} for name in REQUIRED})
    assert result['missing_fields'] == result['review_fields'] == []
    assert result['requires_human_review'] is True
