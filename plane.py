__author__ = 'bdavenport'

import datetime
import json
import time

from datastore import AirCraft

icaoArray = [
                ['011100000000',            'AF', 0, 'Afghanistan',             'Afghanistan.bmp'],
                ['01010000000100',          'AL', 0, 'Albania',                 'Albania.bmp'],
                ['000010100',               'DZ', 0, 'Algeria',                 'Algeria.bmp'],
                ['000010010000',            'AO', 0, 'Angola',                  'Angola.bmp'],
                ['00001100101000',          'AG', 0, 'Antigua and Barbuda',     'Antigua_and_Barbuda.bmp'],
                ['111000',                  'AR', 0, 'Argentina',               'Argentina.bmp'],
                ['01100000000000',          'AM', 0, 'Armenia',                 'Armenia.bmp'],
                ['011111',                  'AU', 0, 'Australia',               'Australia.bmp'],
                ['010001000',               'AT', 0, 'Austria',                 'Austria.bmp'],
                ['01100000000010',          'AZ', 0, 'Azerbaijan',              'Azerbaijan.bmp'],
                ['000010101000',            'BS', 0, 'Bahamas',                 'Bahamas.bmp'],
                ['100010010100',            '', 0, 'Bahrain',                   'Bahrain.bmp'],
                ['011100000010',            'BD', 0, 'Bangladesh',              'Bangladesh.bmp'],
                ['00001010101000',          'BB', 0, 'Barbados',                'Barbados.bmp'],
                ['01010001000000',          'BY', 0, 'Belarus',                 'Belarus.bmp'],
                ['010001001',               'BE', 0, 'Belgium',                 'Belgium.bmp'],
                ['00001010101100',          'BZ', 0, 'Belize',                  'Belize.bmp'],
                ['00001001010000',          'BJ', 0, 'Benin',                   'Benin.bmp'],
                ['01000000000000001',       'BM', 0, 'Bermuda',                 'Bermuda.bmp'],
                ['01000000000000010',       'BM', 0, 'Bermuda',                 'Bermuda.bmp'],
                ['010000000000000110',      'BM', 0, 'Bermuda',                 'Bermuda.bmp'],
                ['0100001001000000',        'BM', 0, 'Bermuda',                 'Bermuda.bmp'],
                ['010000100100000100',      'BM', 0, 'Bermuda',                 'Bermuda.bmp'],
                ['01000010010000010010',    'BM', 0, 'Bermuda',                 'Bermuda.bmp'],
                ['0100001001000001001100',  'BM', 0, 'Bermuda',                 'Bermuda.bmp'],
                ['01000010010000100011',    'BM', 0, 'Bermuda',                 'Bermuda.bmp'],
                ['010000100100001001',      'BM', 0, 'Bermuda',                 'Bermuda.bmp'],
                ['01000010010001011111',    'BM', 0, 'Bermuda',                 'Bermuda.bmp'],
                ['01000010010001100000',    'BM', 0, 'Bermuda',                 'Bermuda.bmp'],
                ['010000100100100011011',   'BM', 0, 'Bermuda',                 'Bermuda.bmp'],
                ['0100001001001000111',     'BM', 0, 'Bermuda',                 'Bermuda.bmp'],
                ['0100001001001001',        'BM', 0, 'Bermuda',                 'Bermuda.bmp'],
                ['0100001110111110100',     'BM', 0, 'Bermuda',                 'Bermuda.bmp'],
                ['01101000000000',          'BT', 0, 'Bhutan',                  'Bhutan.bmp'],
                ['111010010100',            'BO', 0, 'Bolivia',                 'Bolivia.bmp'],
                ['01010001001100',          'BA', 0, 'Bosnia',                  'Bosnia.bmp'],
                ['00000011000000',          'BW', 0, 'Botswana',                'Botswana.bmp'],
                ['111001',                  'BR', 0, 'Brazil',                  'Brazil.bmp'],
                ['10001001010100',          '', 0, 'Brunei',                    'Brunei.bmp'],
                ['010001010',               'BG', 0, 'Bulgaria',                'Bulgaria.bmp'],
                ['000000110010',            'BI', 0, 'Burundi',                 'Burundi.bmp'],
                ['011100001110',            'KH', 0, 'Cambodia',                'Cambodia.bmp'],
                ['000000110100',            'CM', 0, 'Cameroon',                'Cameroon.bmp'],
                ['110000',                  'CA', 0, 'Canada',                  'Canada.bmp'],
                ['1100001',                 'CA', 1, 'Canada Mil',              'Canada_Mil.bmp'],
                ['00001001011000',          'CV', 0, 'Cape Verde',              'Cape_Verde.bmp'],
                ['000001101100',            'CF', 0, 'Central African Republic', 'Central_African_Republic.bmp'],
                ['000010000100',            'TD', 0, 'Chad',                    'Chad.bmp'],
                ['111010000000',            'CL', 0, 'Chile',                   'Chile.bmp'],
                ['1110100000000110',        'CL', 1, 'Chile Mil',               'Chile_Mil.bmp'],
                ['011110',                  'CN', 0, 'China',                   'China.bmp'],
                ['0111100000000001000',     'CN', 0, 'China',                   'China.bmp'],
                ['0111100000000001',        '', 0, 'China Hong Kong',           'China_Hong_Kong.bmp'],
                ['011110000000001000',      '', 0, 'China Hong Kong',           'China_Hong_Kong.bmp'],
                ['011110000000101000100',   '', 0, 'China Hong Kong',           'China_Hong_Kong.bmp'],
                ['011110000000001100111',   '', 0, 'China Macau',               'China_Macau.bmp'],
                ['011110000000001101000',   '', 0, 'China Macau',               'China_Macau.bmp'],
                ['000010101100',            'CO', 0, 'Colombia',                'Colombia.bmp'],
                ['00000011010100',          'KM', 0, 'Comoros',                 'Comoros.bmp'],
                ['000010001100',            'CD', 0, 'Congo-DRC',               'Congo-DRC.bmp'],
                ['000000110110',            'CG', 0, 'Congo-ROC',               'Congo-ROC.bmp'],
                ['10010000000100',          'CK', 0, 'Cook Islands',            'Cook_Islands.bmp'],
                ['000010101110',            'CR', 0, 'Costa Rica',              'Costa_Rica.bmp'],
                ['000000111000',            'CI', 0, "Cote d'Ivoire",           'Cote_dIvoire.bmp'],
                ['01010000000111',          'HR', 0, 'Croatia',                 'Croatia.bmp'],
                ['000010110000',            'CU', 0, 'Cuba',                    'Cuba.bmp'],
                ['01001100100000',          'CY', 0, 'Cyprus',                  'Cyprus.bmp'],
                ['010010011',               'CZ', 0, 'Czech Republic',          'Czech_Republic.bmp'],
                ['010001011',               'DK', 0, 'Denmark',                 'Denmark.bmp'],
                ['00001001100000',          'DJ', 0, 'Djibouti',                'Djibouti.bmp'],
                ['000011000100',            'DO', 0, 'Dominican Republic',      'Dominican_Republic.bmp'],
                ['111010000100',            'EC', 0, 'Ecuador',                 'Ecuador.bmp'],
                ['000000010',               'EG', 0, 'Egypt',                   'Egypt.bmp'],
                ['000010110010',            'SV', 0, 'El Salvador',             'El_Salvador.bmp'],
                ['000001000010',            'GQ', 0, 'Equatorial Guinea',       'Equatorial_Guinea.bmp'],
                ['00100000001000',          'ER', 0, 'Eritrea',                 'Eritrea.bmp'],
                ['01010001000100',          'EE', 0, 'Estonia',                 'Estonia.bmp'],
                ['000001000000',            'ET', 0, 'Ethiopia',                'Ethiopia.bmp'],
                ['110010001000',            'FJ', 0, 'Fiji',                    'Fiji.bmp'],
                ['010001100',               'FI', 0, 'Finland',                 'Finland.bmp'],
                ['001110',                  'FR', 0, 'France',                  'France.bmp'],
                ['000000111110',            'GA', 0, 'Gabon',                   'Gabon.bmp'],
                ['000010011010',            'GM', 0, 'Gambia',                  'Gambia.bmp'],
                ['01010001010000',          'GE', 0, 'Georgia',                 'Georgia.bmp'],
                ['001111',                  'DE', 0, 'Germany',                 'Germany.bmp'],
                ['0011111010',              'DE', 1, 'Germany Mil',             'Germany_Mil.bmp'],
                ['0011111101',              'DE', 1, 'Germany Mil',             'Germany_Mil.bmp'],
                ['0011111110',              'DE', 1, 'Germany Mil',             'Germany_Mil.bmp'],
                ['000001000100',            'DE', 0, 'Ghana',                   'Ghana.bmp'],
                ['010001101',               'GR', 0, 'Greece',                  'Greece.bmp'],
                ['01000110100000',          'GR', 1, 'Greece Mil',              'Greece_Mil.bmp'],
                ['00001100110000',          'GD', 0, 'Grenada',                 'Grenada.bmp'],
                ['000010110100',            'GT', 0, 'Guatemala',               'Guatemala.bmp'],
                ['000001000110',            'GN', 0, 'Guinea',                  'Guinea.bmp'],
                ['00000100100000',          'GW', 0, 'Guinea-Bissau',           'Guinea-Bissau.bmp'],
                ['000010110110',            'GY', 0, 'Guyana',                  'Guyana.bmp'],
                ['000010111000',            'HT', 0, 'Haiti',                   'Haiti.bmp'],
                ['000010111010',            'HN', 0, 'Honduras',                'Honduras.bmp'],
                ['010001110',               'HU', 0, 'Hungary',                 'Hungary.bmp'],
                ['01000111001111000000',    'HU', 1, 'Hungary Mil',             'Hungary_Mil.bmp'],
                ['01000111011111111111',    'HU', 1, 'Hungary Mil',             'Hungary_Mil.bmp'],
                ['111100000',               '', 0, 'ICAO_1',                    'ICAO.bmp'],
                ['11110000100100',          '', 0, 'ICAO_2',                    'ICAO.bmp'],
                ['010011001100',            'IS', 0, 'Iceland',                 'Iceland.bmp'],
                ['100000',                  'IN', 0, 'India',                   'India.bmp'],
                ['1000000000000010',        'IN', 1, 'India Mil',               'India_Mil.bmp'],
                ['100010100',               'ID', 0, 'Indonesia',               'Indonesia.bmp'],
                ['011100110',               'IR', 0, 'Iran',                    'Iran.bmp'],
                ['011100101',               'IQ', 0, 'Iraq',                    'Iraq.bmp'],
                ['010011001010',            'IE', 0, 'Ireland',                 'Ireland.bmp'],
                ['011100111',               'IL', 0, 'Israel',                  'Israel.bmp'],
                ['011100111000101',         'IL', 1, 'Israel Mil',              'Israel_Mil.bmp'],
                ['001100',                  'IT', 0, 'Italy',                   'Italy.bmp'],
                ['0011001111111111',        'IT', 1, 'Italy Mil',               'Italy_Mil.bmp'],
                ['000010111110',            'JM', 0, 'Jamaica',                 'Jamaica.bmp'],
                ['100001',                  'JP', 0, 'Japan',                   'Japan.bmp'],
                ['011101000',               'JO', 0, 'Jordan',                  'Jordan.bmp'],
                ['01101000001100',          'KZ', 0, 'Kazakhstan',              'Kazakhstan.bmp'],
                ['000001001100',            'KE', 0, 'Kenya',                   'Kenya.bmp'],
                ['11001000111000',          'KI', 0, 'Kiribati',                'Kiribati.bmp'],
                ['011100100',               'KP', 0, 'Korea North',             'Korea_North.bmp'],
                ['011100011',               'KR', 0, 'Korea South',             'Korea_South.bmp'],
                ['011100000110',            'KW', 0, 'Kuwait',                  'Kuwait.bmp'],
                ['01100000000100',          'KG', 0, 'Kyrgyzstan',              'Kyrgyzstan.bmp'],
                ['011100001000',            '', 0, 'Laos',                      'Laos.bmp'],
                ['01010000001011',          'LV', 0, 'Latvia',                  'Latvia.bmp'],
                ['011101001',               'LB', 0, 'Lebanon',                 'Lebanon.bmp'],
                ['00000100101000',          'LS', 0, 'Lesotho',                 'Lesotho.bmp'],
                ['000001010000',            'LR', 0, 'Liberia',                 'Liberia.bmp'],
                ['000000011',               'LY', 0, 'Libya',                   'Libya.bmp'],
                ['01010000001111',          'LT', 0, 'Lithuania',               'Lithuania.bmp'],
                ['01001101000000',          'LU', 0, 'Luxembourg',              'Luxembourg.bmp'],
                ['0100110100000011110',     'LU', 1, 'Luxembourg Mil',          'Luxembourg_Mil.bmp'],
                ['01010001001000',          'MK', 0, 'Macedonia',               'Macedonia.bmp'],
                ['000001010100',            'MG', 0, 'Madagascar',              'Madagascar.bmp'],
                ['000001011000',            'MW', 0, 'Malawi',                  'Malawi.bmp'],
                ['011101010',               'MY', 0, 'Malaysia',                'Malaysia.bmp'],
                ['00000101101000',          'MV', 0, 'Maldives',                'Maldives.bmp'],
                ['000001011100',            'ML', 0, 'Mali',                    'Mali.bmp'],
                ['01001101001000',          'MT', 0, 'Malta',                   'Malta.bmp'],
                ['10010000000000',          'MH', 0, 'Marshall Islands',        'Marshall_Islands.bmp'],
                ['00000101111000',          'MR', 0, 'Mauritania',              'Mauritania.bmp'],
                ['00000110000000',          'MU', 0, 'Mauritius',               'Mauritius.bmp'],
                ['000011010',               'MX', 0, 'Mexico',                  'Mexico.bmp'],
                ['01101000000100',          'FM', 0, 'Micronesia',              'Micronesia.bmp'],
                ['01010000010011',          'MD', 0, 'Moldova',                 'Moldova.bmp'],
                ['01001101010000',          'MC', 0, 'Monaco',                  'Monaco.bmp'],
                ['01101000001000',          'MN', 0, 'Mongolia',                'Mongolia.bmp'],
                ['01010001011000',          'ME', 0, 'Montenegro',              'Montenegro.bmp'],
                ['000000100',               'MA', 0, 'Morocco',                 'Morocco.bmp'],
                ['00000010000000001011',    'MA', 1, 'Morocco Mil',             'Morocco_Mil.bmp'],
                ['000000000110',            'MZ', 0, 'Mozambique',              'Mozambique.bmp'],
                ['011100000100',            'MM', 0, 'Myanmar',                 'Myanmar.bmp'],
                ['00100000000100',          'NA', 0, 'Namibia',                 'Namibia.bmp'],
                ['11001000101000',          'NR', 0, 'Nauru',                   'Nauru.bmp'],
                ['011100001010',            'NP', 0, 'Nepal',                   'Nepal.bmp'],
                ['010010000',               'NL', 0, 'Netherlands',             'Netherlands.bmp'],
                ['010010000000',            'NL', 1, 'Netherlands Mil',         'Netherlands_Mil.bmp'],
                ['110010000',               'NZ', 0, 'New Zealand',             'New_Zealand.bmp'],
                ['000011000000',            'NI', 0, 'Nicaragua',               'Nicaragua.bmp'],
                ['000001100010',            'NE', 0, 'Niger',                   'Niger.bmp'],
                ['000001100100',            'NG', 0, 'Nigeria',                 'Nigeria.bmp'],
                ['010001111',               'NO', 0, 'Norway',                  'Norway.bmp'],
                ['01110000110000',          'OM', 0, 'Oman',                    'Oman.bmp'],
                ['01110000110000000111',    'OM', 1, 'Oman Mil',                'Oman_Mil.bmp'],
                ['011101100',               'PK', 0, 'Pakistan',                'Pakistan.bmp'],
                ['01101000010000',          'PW', 0, 'Palau',                   'Palau.bmp'],
                ['000011000010',            'PA', 0, 'Panama',                  'Panama.bmp'],
                ['100010011000',            'PG', 0, 'Papua New Guinea',        'Papua_New_Guinea.bmp'],
                ['111010001000',            'PY', 0, 'Paraguay',                'Paraguay.bmp'],
                ['111010001100',            'PE', 0, 'Peru',                    'Peru.bmp'],
                ['011101011',               'PH', 0, 'Philippines',             'Philippines.bmp'],
                ['010010001',               'PL', 0, 'Poland',                  'Poland.bmp'],
                ['0100100011011000',        'PL', 1, 'Poland Mil',              'Poland_Mil.bmp'],
                ['010010010',               'PT', 0, 'Portugal',                'Portugal.bmp'],
                ['0100100101111100',        'PT', 1, 'Portugal Mil',            'Portugal_Mil.bmp'],
                ['00000110101000',          'QA', 0, 'Qatar',                   'Qatar.bmp'],
                ['010010100',               'RO', 0, 'Romania',                 'Romania.bmp'],
                ['0001',                    'RU', 0, 'Russia',                  'Russia.bmp'],
                ['000001101110',            'RW', 0, 'Rwanda',                  'Rwanda.bmp'],
                ['10010000001000',          'WS', 0, 'Samoa',                   'Samoa.bmp'],
                ['01010000000000',          'SM', 0, 'San Marino',              'San_Marino.bmp'],
                ['00001001111000',          'ST', 0, 'Sao Tome Principe',       'Sao_Tome_Principe.bmp'],
                ['011100010',               'SA', 0, 'Saudi Arabia',            'Saudi_Arabia.bmp'],
                ['000001110000',            'SN', 0, 'Senegal',                 'Senegal.bmp'],
                ['010011000',               'RS', 0, 'Serbia',                  'Serbia.bmp'],
                ['00000111010000',          'SC', 0, 'Seychelles',              'Seychelles.bmp'],
                ['00000111011000',          'SL', 0, 'Sierra Leone',            'Sierra_Leone.bmp'],
                ['011101101',               'SG', 0, 'Singapore',               'Singapore.bmp'],
                ['01010000010111',          'SK', 0, 'Slovakia',                'Slovakia.bmp'],
                ['01010000011011',          'SI', 0, 'Slovenia',                'Slovenia.bmp'],
                ['0101000001101111',        'SI', 1, 'Slovenia Mil',            'Slovenia_Mil.bmp'],
                ['10001001011100',          'SB', 0, 'Solomon Islands',         'Solomon_Islands.bmp'],
                ['000001111000',            'SO', 0, 'Somalia',                 'Somalia.bmp'],
                ['000000001',               'ZA', 0, 'South Afric',             'South_Africa.bmp'],
                ['001101',                  'ES', 0, 'Spain',                   'Spain.bmp'],
                ['00110101',                'ES', 1, 'Spain Mil',               'Spain_Mil.bmp'],
                ['0011011',                 'ES', 1, 'Spain Mil',               'Spain_Mil.bmp'],
                ['011101110',               'LK', 0, 'Sri Lanka',               'Sri_Lanka.bmp'],
                ['011101110',               'LC', 0, 'St Lucia',                'St_Lucia.bmp'],
                ['00001011110000',          'VC', 0, 'St Vincent',              'St_Vincent.bmp'],
                ['000001111100',            'SD', 0, 'Sudan',                   'Sudan.bmp'],
                ['000011001000',            'SR', 0, 'Suriname',                'Suriname.bmp'],
                ['00000111101000',          'SZ', 0, 'Swaziland',               'Swaziland.bmp'],
                ['010010101',               'SE', 0, 'Sweden',                  'Sweden.bmp'],
                ['010010110',               'CH', 0, 'Switzerland',             'Switzerland.bmp'],
                ['010010110111',            'CH', 1, 'Switzerland Mil',         'Switzerland_Mil.bmp'],

                ['1010',                    'US', 0, 'USA',                     'United_States.bmp'],
                ['1010111',                 'US', 1, 'USA MIL',                 'United_States_Mil.bmp'],
                ['1010110111111',           'US', 1, 'USA MIL',                 'United_States_Mil.bmp'],
                ['1010110111110111111',     'US', 1, 'USA MIL',                 'United_States_Mil.bmp'],
                ['10101101111101111101',    'US', 1, 'USA MIL',                 'United_States_Mil.bmp'],
                ['101011011111011111001',   'US', 1, 'USA MIL',                 'United_States_Mil.bmp'],
            ]

# Lets make a plane
class Plane():
    def generateJSON(self):
        self.lookupCountry()
        self.lookupType()
        dumpthis = {}
        dumpthis['icao'] = self.icao
        dumpthis['country'] = self.country
        dumpthis['country_short'] = self.country_short
        dumpthis['country_flag'] = self.country_flag
        dumpthis['type'] = self.type
        dumpthis['operator'] = self.operator
        dumpthis['registration'] = self.registration
        dumpthis['military'] = self.isMilitary
        return json.dumps(dumpthis, sort_keys=True, indent=4)

    # This is our plane, there shall be non other like it (hopefully).
    def __init__(self):
        # Session instance of found plane, database driven, int
        self.session = False

        # icao (6) and Flight(8) codes,
        self.icao = False
        self.flightid = False

        # Altitude, GroundSpeed, and Track, ints
        self.altitude = None
        self.groundspeed = None
        self.track = None

        # Where are they? floats
        self.latitude = None
        self.longitude = None

        # Vertical Rate, altitude changes? int
        self.virticalrate = 0

        # Squawk
        self.squawk = False

        # Squawk Alert
        self.squawkalert = False

        # Emergency
        self.emergency = False

        # SPI (Ident) transponder
        self.spi = False

        # On the ground?
        self.isOnGround = False

        # Last time we updated any data
        self.seen_start = datetime.datetime.utcnow()
        self.lastupdate = datetime.datetime.utcnow()

        # This is the number of msgs, JSON count is number of msgs by json...
        self.msgcount = 0
        self.msgcountJSON = 0

        # Is this plane in the KML/JSON?
        self.showKML = True

        self.trail = []

        self.signal = []

        # Extra plane info, that has to be looked up
        self.country = False
        self.country_short = False
        self.country_flag = False
        self.type = False
        self.model = False
        self.operator = False
        self.registration = False
        self.isMilitary = False


    def lookupCountry(self):
        # This is manually converted from data/Countries.dat
        me = int(self.icao, 16)
        for country in icaoArray:
            high = int(country[0].ljust(24, "1"), 2)
            low = int(country[0].ljust(24, "0"), 2)
            if (high >= me) and (me >= low):
                self.country = country[3]
                self.country_sort = country[1]
                self.country_flag = country[4]
                self.isMilitary = bool(country[2])
                break


    def lookupType(self):
        query = AirCraft.query(AirCraft.icao24 == self.icao).fetch()
        if len(query) == 0:
            time.sleep(1)
            query = AirCraft.query(AirCraft.icao24 == self.icao).fetch()
        self.type = query[0].typeCode
        self.model = query[0].model
        self.operator = query[0].operator
        self.registration = query[0].registration
