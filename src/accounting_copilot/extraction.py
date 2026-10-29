"""Deterministic review signals for provider fields, never approval authority."""
import math

REQUIRED = ('VendorName', 'InvoiceId', 'InvoiceDate', 'SubTotal', 'TotalTax', 'InvoiceTotal')


def review_fields(fields):
    rows, missing, low = [], [], []
    for name in REQUIRED:
        field = fields.get(name, {})
        value = next((field[k] for k in ('valueCurrency', 'valueDate', 'valueString', 'valueNumber', 'content')
                      if field.get(k) is not None), None)
        confidence = field.get('confidence')
        if type(confidence) not in (int, float) or not math.isfinite(confidence) or not 0 <= confidence <= 1:
            confidence = None
        if value is None or value == '':
            missing.append(name)
        if confidence is None or confidence < .8:
            low.append(name)
        rows.append({'field': name, 'value': value, 'provider_confidence': confidence})
    return {'fields': rows, 'missing_fields': missing, 'review_fields': low,
            'recommendation': 'Check every value against the source; map supplier identity independently',
            'confidence_note': 'Provider confidence is uncalibrated; 0.8 is a demo review threshold, not accuracy',
            'requires_human_review': True}
