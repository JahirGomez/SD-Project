from zeep import Client

def get_country_info(country_code):
    wsdl = 'http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL'
    client = Client(wsdl)
    response = client.service.FullCountryInfo(country_code)
    return {
        'name': response.sName,
        'currency': response.sCurrencyISOCode,
        'capital': response.sCapitalCity,
        'continent': response.sContinentCode,
        'phone_code': response.sPhoneCode
    }