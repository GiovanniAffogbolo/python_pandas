
from pytest import fixture

from exchanges import BiosphereExchange, ExchangeProcessor, TechnosphereExchange


@fixture
def valid_biosphere_exchange():
    return BiosphereExchange(1, 12, 'kg', 'compartment')
    
@fixture
def valid_technosphere_exchange():
    return TechnosphereExchange(1, 12, 'kg')

@fixture
def valid_exchange_processor():
    return ExchangeProcessor()