__author__ = 'bdavenport'

import datetime
import json
import time

from datastore import Aircraft

# These are to make beast guesses as to where there from, or to look up extra data
icaoArray = [
                ['011100000000',            'AF',   0, 'Afghanistan',             'Afghanistan.png'],
                ['01010000000100',          'AL',   0, 'Albania',                 'Albania.png'],
                ['000010100',               'DZ',   0, 'Algeria',                 'Algeria.png'],
                ['000010010000',            'AO',   0, 'Angola',                  'Angola.png'],
                ['00001100101000',          'AG',   0, 'Antigua and Barbuda',     'Antigua_and_Barbuda.png'],
                ['111000',                  'AR',   0, 'Argentina',               'Argentina.png'],
                ['01100000000000',          'AM',   0, 'Armenia',                 'Armenia.png'],
                ['011111',                  'AU',   0, 'Australia',               'Australia.png'],
                ['010001000',               'AT',   0, 'Austria',                 'Austria.png'],
                ['01100000000010',          'AZ',   0, 'Azerbaijan',              'Azerbaijan.png'],
                ['000010101000',            'BS',   0, 'Bahamas',                 'Bahamas.png'],
                ['100010010100',            '',     0, 'Bahrain',                 'Bahrain.png'],
                ['011100000010',            'BD',   0, 'Bangladesh',              'Bangladesh.png'],
                ['00001010101000',          'BB',   0, 'Barbados',                'Barbados.png'],
                ['01010001000000',          'BY',   0, 'Belarus',                 'Belarus.png'],
                ['010001001',               'BE',   0, 'Belgium',                 'Belgium.png'],
                ['00001010101100',          'BZ',   0, 'Belize',                  'Belize.png'],
                ['00001001010000',          'BJ',   0, 'Benin',                   'Benin.png'],
                ['01000000000000001',       'BM',   0, 'Bermuda',                 'Bermuda.png'],
                ['01000000000000010',       'BM',   0, 'Bermuda',                 'Bermuda.png'],
                ['010000000000000110',      'BM',   0, 'Bermuda',                 'Bermuda.png'],
                ['0100001001000000',        'BM',   0, 'Bermuda',                 'Bermuda.png'],
                ['010000100100000100',      'BM',   0, 'Bermuda',                 'Bermuda.png'],
                ['01000010010000010010',    'BM',   0, 'Bermuda',                 'Bermuda.png'],
                ['0100001001000001001100',  'BM',   0, 'Bermuda',                 'Bermuda.png'],
                ['01000010010000100011',    'BM',   0, 'Bermuda',                 'Bermuda.png'],
                ['010000100100001001',      'BM',   0, 'Bermuda',                 'Bermuda.png'],
                ['01000010010001011111',    'BM',   0, 'Bermuda',                 'Bermuda.png'],
                ['01000010010001100000',    'BM',   0, 'Bermuda',                 'Bermuda.png'],
                ['010000100100100011011',   'BM',   0, 'Bermuda',                 'Bermuda.png'],
                ['0100001001001000111',     'BM',   0, 'Bermuda',                 'Bermuda.png'],
                ['0100001001001001',        'BM',   0, 'Bermuda',                 'Bermuda.png'],
                ['0100001110111110100',     'BM',   0, 'Bermuda',                 'Bermuda.png'],
                ['01101000000000',          'BT',   0, 'Bhutan',                  'Bhutan.png'],
                ['111010010100',            'BO',   0, 'Bolivia',                 'Bolivia.png'],
                ['01010001001100',          'BA',   0, 'Bosnia',                  'Bosnia.png'],
                ['00000011000000',          'BW',   0, 'Botswana',                'Botswana.png'],
                ['111001',                  'BR',   0, 'Brazil',                  'Brazil.png'],
                ['10001001010100',          '',     0, 'Brunei',                  'Brunei.png'],
                ['010001010',               'BG',   0, 'Bulgaria',                'Bulgaria.png'],
                ['000010011100',            'BF',   0, 'Burkina Faso',            'Burkina_Faso.png'],
                ['000000110010',            'BI',   0, 'Burundi',                 'Burundi.png'],
                ['011100001110',            'KH',   0, 'Cambodia',                'Cambodia.png'],
                ['000000110100',            'CM',   0, 'Cameroon',                'Cameroon.png'],
                ['110000',                  'CA',   0, 'Canada',                  'Canada.png'],
                ['1100001',                 'CA',   1, 'Canada Mil',              'Canada_Mil.png'],
                ['00001001011000',          'CV',   0, 'Cape Verde',              'Cape_Verde.png'],
                ['000001101100',            'CF',   0, 'Central African Republic','Central_African_Republic.png'],
                ['000010000100',            'TD',   0, 'Chad',                    'Chad.png'],
                ['111010000000',            'CL',   0, 'Chile',                   'Chile.png'],
                ['1110100000000110',        'CL',   1, 'Chile Mil',               'Chile_Mil.png'],
                ['011110',                  'CN',   0, 'China',                   'China.png'],
                ['0111100000000001000',     'CN',   0, 'China',                   'China.png'],
                ['0111100000000001',        '',     0, 'China (Hong Kong)',       'China_Hong_Kong.png'],
                ['011110000000001000',      '',     0, 'China (Hong Kong)',       'China_Hong_Kong.png'],
                ['011110000000101000100',   '',     0, 'China (Hong Kong)',       'China_Hong_Kong.png'],
                ['011110000000001100111',   '',     0, 'China (Macau)',           'China_Macau.png'],
                ['011110000000001101000',   '',     0, 'China (Macau)',           'China_Macau.png'],
                ['000010101100',            'CO',   0, 'Colombia',                'Colombia.png'],
                ['00000011010100',          'KM',   0, 'Comoros',                 'Comoros.png'],
                ['000010001100',            'CD',   0, 'Congo-DRC',               'Congo-DRC.png'],
                ['000000110110',            'CG',   0, 'Congo-ROC',               'Congo-ROC.png'],
                ['10010000000100',          'CK',   0, 'Cook Islands',            'Cook_Islands.png'],
                ['000010101110',            'CR',   0, 'Costa Rica',              'Costa_Rica.png'],
                ['000000111000',            'CI',   0, "Cote d'Ivoire",           'Cote_dIvoire.png'],
                ['01010000000111',          'HR',   0, 'Croatia',                 'Croatia.png'],
                ['000010110000',            'CU',   0, 'Cuba',                    'Cuba.png'],
                ['01001100100000',          'CY',   0, 'Cyprus',                  'Cyprus.png'],
                ['010010011',               'CZ',   0, 'Czech Republic',          'Czech_Republic.png'],
                ['010001011',               'DK',   0, 'Denmark',                 'Denmark.png'],
                ['00001001100000',          'DJ',   0, 'Djibouti',                'Djibouti.png'],
                ['000011000100',            'DO',   0, 'Dominican Republic',      'Dominican_Republic.png'],
                ['111010000100',            'EC',   0, 'Ecuador',                 'Ecuador.png'],
                ['000000010',               'EG',   0, 'Egypt',                   'Egypt.png'],
                ['00000001000000000111000', 'EG',   0, 'Egypt',                   'Egypt.png'],
                ['00000001000000001000111', 'EG',   0, 'Egypt',                   'Egypt.png'],
                ['00000001000000000111',    'EG',   1, 'Egypt Mil',               'Egypt_Mil.png'],
                ['00000001000000001000',    'EG',   1, 'Egypt Mil',               'Egypt_Mil.png'],
                ['000000010',               'EG',   0, 'Egypt',                   'Egypt.png'],
                ['000000010',               'EG',   0, 'Egypt',                   'Egypt.png'],
                ['000010110010',            'SV',   0, 'El Salvador',             'El_Salvador.png'],
                ['000001000010',            'GQ',   0, 'Equatorial Guinea',       'Equatorial_Guinea.png'],
                ['00100000001000',          'ER',   0, 'Eritrea',                 'Eritrea.png'],
                ['01010001000100',          'EE',   0, 'Estonia',                 'Estonia.png'],
                ['000001000000',            'ET',   0, 'Ethiopia',                'Ethiopia.png'],
                ['110010001000',            'FJ',   0, 'Fiji',                    'Fiji.png'],
                ['010001100',               'FI',   0, 'Finland',                 'Finland.png'],
                ['001110',                  'FR',   0, 'France',                  'France.png'],
                ['000000111110',            'GA',   0, 'Gabon',                   'Gabon.png'],
                ['000010011010',            'GM',   0, 'Gambia',                  'Gambia.png'],
                ['01010001010000',          'GE',   0, 'Georgia',                 'Georgia.png'],
                ['001111',                  'DE',   0, 'Germany',                 'Germany.png'],
                ['0011111010',              'DE',   1, 'Germany Mil',             'Germany_Mil.png'],
                ['0011111101',              'DE',   1, 'Germany Mil',             'Germany_Mil.png'],
                ['0011111110',              'DE',   1, 'Germany Mil',             'Germany_Mil.png'],
                ['000001000100',            'DE',   0, 'Ghana',                   'Ghana.png'],
                ['010001101',               'GR',   0, 'Greece',                  'Greece.png'],
                ['01000110100000',          'GR',   1, 'Greece Mil',              'Greece_Mil.png'],
                ['00001100110000',          'GD',   0, 'Grenada',                 'Grenada.png'],
                ['000010110100',            'GT',   0, 'Guatemala',               'Guatemala.png'],
                ['000001000110',            'GN',   0, 'Guinea',                  'Guinea.png'],
                ['00000100100000',          'GW',   0, 'Guinea-Bissau',           'Guinea-Bissau.png'],
                ['000010110110',            'GY',   0, 'Guyana',                  'Guyana.png'],
                ['000010111000',            'HT',   0, 'Haiti',                   'Haiti.png'],
                ['000010111010',            'HN',   0, 'Honduras',                'Honduras.png'],
                ['010001110',               'HU',   0, 'Hungary',                 'Hungary.png'],
                ['01000111001111000000',    'HU',   1, 'Hungary Mil',             'Hungary_Mil.png'],
                ['01000111011111111111',    'HU',   1, 'Hungary Mil',             'Hungary_Mil.png'],
                ['111100000',               '',     0, 'ICAO_1',                  'ICAO.png'],
                ['11110000100100',          '',     0, 'ICAO_2',                  'ICAO.png'],
                ['010011001100',            'IS',   0, 'Iceland',                 'Iceland.png'],
                ['100000',                  'IN',   0, 'India',                   'India.png'],
                ['1000000000000010',        'IN',   1, 'India Mil',               'India_Mil.png'],
                ['100010100',               'ID',   0, 'Indonesia',               'Indonesia.png'],
                ['011100110',               'IR',   0, 'Iran',                    'Iran.png'],
                ['011100101',               'IQ',   0, 'Iraq',                    'Iraq.png'],
                ['010011001010',            'IE',   0, 'Ireland',                 'Ireland.png'],
                ['01000011111001110001011', 'IM',   0, 'Isle of Man',             'Isle_of_Man.png'],
                ['010000111110011100011',   'IM',   0, 'Isle of Man',             'Isle_of_Man.png'],
                ['0100001111100111001',     'IM',   0, 'Isle of Man',             'Isle_of_Man.png'],
                ['010000111110011101',      'IM',   0, 'Isle of Man',             'Isle_of_Man.png'],
                ['01000011111001111',       'IM',   0, 'Isle of Man',             'Isle_of_Man.png'],
                ['010011100011100',         'IM',   0, 'Isle of Man',             'Isle_of_Man.png'],
                ['0100111000111010',        'IM',   0, 'Isle of Man',             'Isle_of_Man.png'],
                ['011100111',               'IL',   0, 'Israel',                  'Israel.png'],
                ['011100111000101',         'IL',   1, 'Israel Mil',              'Israel_Mil.png'],
                ['001100',                  'IT',   0, 'Italy',                   'Italy.png'],
                ['0011001111111111',        'IT',   1, 'Italy Mil',               'Italy_Mil.png'],
                ['000010111110',            'JM',   0, 'Jamaica',                 'Jamaica.png'],
                ['100001',                  'JP',   0, 'Japan',                   'Japan.png'],
                ['011101000',               'JO',   0, 'Jordan',                  'Jordan.png'],
                ['01101000001100',          'KZ',   0, 'Kazakhstan',              'Kazakhstan.png'],
                ['000001001100',            'KE',   0, 'Kenya',                   'Kenya.png'],
                ['11001000111000',          'KI',   0, 'Kiribati',                'Kiribati.png'],
                ['011100100',               'KP',   0, 'Korea North',             'Korea_North.png'],
                ['011100011',               'KR',   0, 'Korea South',             'Korea_South.png'],
                ['011100000110',            'KW',   0, 'Kuwait',                  'Kuwait.png'],
                ['01100000000100',          'KG',   0, 'Kyrgyzstan',              'Kyrgyzstan.png'],
                ['011100001000',            '',     0, 'Laos',                    'Laos.png'],
                ['01010000001011',          'LV',   0, 'Latvia',                  'Latvia.png'],
                ['011101001',               'LB',   0, 'Lebanon',                 'Lebanon.png'],
                ['00000100101000',          'LS',   0, 'Lesotho',                 'Lesotho.png'],
                ['000001010000',            'LR',   0, 'Liberia',                 'Liberia.png'],
                ['000000011',               'LY',   0, 'Libya',                   'Libya.png'],
                ['01010000001111',          'LT',   0, 'Lithuania',               'Lithuania.png'],
                ['01001101000000',          'LU',   0, 'Luxembourg',              'Luxembourg.png'],
                ['0100110100000011110',     'LU',   1, 'Luxembourg Mil',          'Luxembourg_Mil.png'],
                ['01010001001000',          'MK',   0, 'Macedonia',               'Macedonia.png'],
                ['000001010100',            'MG',   0, 'Madagascar',              'Madagascar.png'],
                ['000001011000',            'MW',   0, 'Malawi',                  'Malawi.png'],
                ['011101010',               'MY',   0, 'Malaysia',                'Malaysia.png'],
                ['00000101101000',          'MV',   0, 'Maldives',                'Maldives.png'],
                ['000001011100',            'ML',   0, 'Mali',                    'Mali.png'],
                ['01001101001000',          'MT',   0, 'Malta',                   'Malta.png'],
                ['10010000000000',          'MH',   0, 'Marshall Islands',        'Marshall_Islands.png'],
                ['00000101111000',          'MR',   0, 'Mauritania',              'Mauritania.png'],
                ['00000110000000',          'MU',   0, 'Mauritius',               'Mauritius.png'],
                ['000011010',               'MX',   0, 'Mexico',                  'Mexico.png'],
                ['01101000000100',          'FM',   0, 'Micronesia',              'Micronesia.png'],
                ['01010000010011',          'MD',   0, 'Moldova',                 'Moldova.png'],
                ['01001101010000',          'MC',   0, 'Monaco',                  'Monaco.png'],
                ['01101000001000',          'MN',   0, 'Mongolia',                'Mongolia.png'],
                ['01010001011000',          'ME',   0, 'Montenegro',              'Montenegro.png'],
                ['000000100',               'MA',   0, 'Morocco',                 'Morocco.png'],
                ['00000010000000001011',    'MA',   1, 'Morocco Mil',             'Morocco_Mil.png'],
                ['000000000110',            'MZ',   0, 'Mozambique',              'Mozambique.png'],
                ['011100000100',            'MM',   0, 'Myanmar',                 'Myanmar.png'],
                ['00100000000100',          'NA',   0, 'Namibia',                 'Namibia.png'],
                ['11001000101000',          'NR',   0, 'Nauru',                   'Nauru.png'],
                ['011100001010',            'NP',   0, 'Nepal',                   'Nepal.png'],
                ['010010000',               'NL',   0, 'Netherlands',             'Netherlands.png'],
                ['010010000000',            'NL',   1, 'Netherlands Mil',         'Netherlands_Mil.png'],
                ['110010000',               'NZ',   0, 'New Zealand',             'New_Zealand.png'],
                ['000011000000',            'NI',   0, 'Nicaragua',               'Nicaragua.png'],
                ['000001100010',            'NE',   0, 'Niger',                   'Niger.png'],
                ['000001100100',            'NG',   0, 'Nigeria',                 'Nigeria.png'],
                ['010001111',               'NO',   0, 'Norway',                  'Norway.png'],
                ['01110000110000',          'OM',   0, 'Oman',                    'Oman.png'],
                ['01110000110000000111',    'OM',   1, 'Oman Mil',                'Oman_Mil.png'],
                ['011101100',               'PK',   0, 'Pakistan',                'Pakistan.png'],
                ['01101000010000',          'PW',   0, 'Palau',                   'Palau.png'],
                ['000011000010',            'PA',   0, 'Panama',                  'Panama.png'],
                ['100010011000',            'PG',   0, 'Papua New Guinea',        'Papua_New_Guinea.png'],
                ['111010001000',            'PY',   0, 'Paraguay',                'Paraguay.png'],
                ['111010001100',            'PE',   0, 'Peru',                    'Peru.png'],
                ['011101011',               'PH',   0, 'Philippines',             'Philippines.png'],
                ['010010001',               'PL',   0, 'Poland',                  'Poland.png'],
                ['0100100011011000',        'PL',   1, 'Poland Mil',              'Poland_Mil.png'],
                ['010010010',               'PT',   0, 'Portugal',                'Portugal.png'],
                ['0100100101111100',        'PT',   1, 'Portugal Mil',            'Portugal_Mil.png'],
                ['00000110101000',          'QA',   0, 'Qatar',                   'Qatar.png'],
                ['010010100',               'RO',   0, 'Romania',                 'Romania.png'],
                ['0001',                    'RU',   0, 'Russia',                  'Russia.png'],
                ['000001101110',            'RW',   0, 'Rwanda',                  'Rwanda.png'],
                ['10010000001000',          'WS',   0, 'Samoa',                   'Samoa.png'],
                ['01010000000000',          'SM',   0, 'San Marino',              'San_Marino.png'],
                ['00001001111000',          'ST',   0, 'Sao Tome and Principe',   'Sao_Tome_Principe.png'],
                ['011100010',               'SA',   0, 'Saudi Arabia',            'Saudi_Arabia.png'],
                ['000001110000',            'SN',   0, 'Senegal',                 'Senegal.png'],
                ['010011000',               'RS',   0, 'Serbia',                  'Serbia.png'],
                ['00000111010000',          'SC',   0, 'Seychelles',              'Seychelles.png'],
                ['00000111011000',          'SL',   0, 'Sierra Leone',            'Sierra_Leone.png'],
                ['011101101',               'SG',   0, 'Singapore',               'Singapore.png'],
                ['01010000010111',          'SK',   0, 'Slovakia',                'Slovakia.png'],
                ['01010000011011',          'SI',   0, 'Slovenia',                'Slovenia.png'],
                ['0101000001101111',        'SI',   1, 'Slovenia Mil',            'Slovenia_Mil.png'],
                ['10001001011100',          'SB',   0, 'Solomon Islands',         'Solomon_Islands.png'],
                ['000001111000',            'SO',   0, 'Somalia',                 'Somalia.png'],
                ['000000001',               'ZA',   0, 'South Africa',            'South_Africa.png'],
                ['001101',                  'ES',   0, 'Spain',                   'Spain.png'],
                ['00110101',                'ES',   1, 'Spain Mil',               'Spain_Mil.png'],
                ['0011011',                 'ES',   1, 'Spain Mil',               'Spain_Mil.png'],
                ['011101110',               'LK',   0, 'Sri Lanka',               'Sri_Lanka.png'],
                ['011101110',               'LC',   0, 'St Lucia',                'St_Lucia.png'],
                ['00001011110000',          'VC',   0, 'St Vincent',              'St_Vincent.png'],
                ['000001111100',            'SD',   0, 'Sudan',                   'Sudan.png'],
                ['000011001000',            'SR',   0, 'Suriname',                'Suriname.png'],
                ['00000111101000',          'SZ',   0, 'Swaziland',               'Swaziland.png'],
                ['010010101',               'SE',   0, 'Sweden',                  'Sweden.png'],
                ['010010110',               'CH',   0, 'Switzerland',             'Switzerland.png'],
                ['010010110111',            'CH',   1, 'Switzerland Mil',         'Switzerland_Mil.png'],
                ['011101111',               '',     0, 'Syria',                   'Syria.png'],
                ['10001001100100',          '',     0, 'Taiwan',                   'Taiwan.png'],
                ['01010001010100',          '',     0, 'Tajikistan',               'Tajikistan.png'],
                ['000010000000',            '',     0, 'Tanzania',                 'Tanzania.png'],
                ['100010000',               '',     0, 'Thailand',                 'Thailand.png'],
                ['000010001000',            '',     0, 'Togo',                     'Togo.png'],
                ['11001000110100',          '',     0, 'Tonga',                    'Tonga.png'],
                ['000011000110',            '',     0, 'Trinidad and Tobago',      'Trinidad_and_Tobago.png'],
                ['000000101',               '',     0, 'Tunisia',                  'Tunisia.png'],
                ['010010111',               '',     0, 'Turkey',                   'Turkey.png'],
                ['0100101110000010',        '',     1, 'Turkey Mil',               'Turkey_Mil.png'],
                ['01100000000110',          '',     0, 'Turkmenistan',             'Turkmenistan.png'],
                ['000001101000',            '',     0, 'Uganda',                   'Uganda.png'],
                ['010100001',               '',     0, 'Ukraine',                  'Ukraine.png'],
                ['100010010110',            '',     0, 'United Arab Emirates',     'United_Arab_Emirates.png'],
                ['010000',                  '',     0, 'United Kingdom',           'United_Kingdom.png'],
                ['0100001111',              '',     1, 'United Kingdom Mil',       'United_Kingdom_Mil.png'],
                ['010000000000000000',      '',     1, 'United Kingdom Mil',       'United_Kingdom_Mil.png'],
                ['1010',                    'US',   0, 'United States',                     'United_States.png'],
                ['1010111',                 'US',   1, 'United States Mil',                 'United_States_Mil.png'],
                ['1010110111111',           'US',   1, 'United States Mil',                 'United_States_Mil.png'],
                ['1010110111110111111',     'US',   1, 'United States Mil',                 'United_States_Mil.png'],
                ['10101101111101111101',    'US',   1, 'United States Mil',                 'United_States_Mil.png'],
                ['101011011111011111001',   'US',   1, 'United States Mil',                 'United_States_Mil.png'],
                ['111010010000',            '',     0, 'Uruguay',                  'Uruguay.png'],
                ['01010000011111',          '',     0, 'Uzbekistan',               'Uzbekistan.png'],
                ['11001001000000',          '',     0, 'Vanuatu',                  'Vanuatu.png'],
                ['000011011',               '',     0, 'Venezuela',                'Venezuela.png'],
                ['100010001',               '',     0, 'Viet-Nam',                 'Viet-Nam.png'],
                ['100010010000',            '',     0, 'Yemen',                    'Yemen.png'],
                ['000010001010',            '',     0, 'Zambia',                   'Zambia.png'],
                ['00000000010000',          '',     0, 'Zimbabwe',                 'Zimbabwe.png'],
                ['0','',0,'','NoFlag.png'],
                ['1','',0,'','NoFlag.png'],
            ]

# Lets make a plane
class Plane():
    def generateJSON(self):
        self.lookupCountry()
        self.lookupType()
        dumpthis = {}
        dumpthis['comment1'] = "Data provided by http://pp-sqb.mantma.co.uk/ with their permission"
        dumpthis['icao'] = self.icao
        dumpthis['country'] = self.country
        dumpthis['country_short'] = self.country_short
        dumpthis['country_flag'] = self.country_flag
        dumpthis['type'] = self.type
        dumpthis['operator'] = self.operator
        dumpthis['registration'] = self.registration
        dumpthis['is_military'] = self.isMilitary
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
        self.country_flag = "NoFlag.png"
        self.type = "@@@"
        self.model = False
        self.operator = "@@@"
        self.registration = "NO-REG"
        self.isMilitary = False


    def lookupCountry(self):
        # This is manually converted from data/Countries.dat
        # TODO: Check to see if this data is in datastore already.
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
        query = Aircraft.query(Aircraft.icao == self.icao).fetch()
        if len(query) == 0:
            time.sleep(1)
            query = Aircraft.query(Aircraft.icao == self.icao).fetch()
        self.type = query[0].icao_type
        if query[0].operator_flag == '':
            query[0].operator_flag = "@@@"
            query[0].put()
        self.operator = query[0].operator_flag
        self.registration = query[0].registration
