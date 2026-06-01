

from exchanges import BiosphereExchange, ExchangeProcessor, TechnosphereExchange

def test_valid_technosphere_exchange_passes_validation(valid_technosphere_exchange):
    assert valid_technosphere_exchange.validate()

def test_technosphere_exchange_with_negative_amount_fails_validation(valid_technosphere_exchange): 
    valid_technosphere_exchange.amount = -12
    assert not valid_technosphere_exchange.validate()

def test_biosphere_exchange_with_no_compartment_fails_validation(valid_biosphere_exchange):
    valid_biosphere_exchange.compartment = ''
    assert not valid_biosphere_exchange.validate()

def test_biosphere_exchange_with_no_unit_fails_validation(valid_biosphere_exchange):
    valid_biosphere_exchange.unit = ''
    assert not valid_biosphere_exchange.validate()

def test_get_summary_counts_validated_exchanges(tmp_path):
    csv = tmp_path / "test.csv"
    csv.write_text(
        "activity_id,amount,unit,type,compartment\n"
        "A1,10,kg,technosphere,\n"
    )
    processor = ExchangeProcessor(str(csv))
    processor.load()
    processor.validate_all()
    assert processor.get_summary() == {"total": 1, "validated": 1}