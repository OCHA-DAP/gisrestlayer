import datetime

UPDATE_FREQ_DICT = {
    '1': 'Every day',
    '7': 'Every week',
    '14': 'Every two weeks',
    '30': 'Every month',
    '90': 'Every three months',
    '180': 'Every six months',
    '365': 'Every year',
    '0': 'Live',
    '-2': 'As needed',
    '-1': 'Never',
}

LICENSES_DICT = {
    'cc-by': 'Creative Commons Attribution International',
    'cc-by-igo': 'Creative Commons Attribution for Intergovernmental Organisations',
    'hdx-multi': 'Multiple Licenses',
    'hdx-other': 'Other',
    'hdx-odc-odbl': 'Open Database License (ODC-ODbL)',
    'hdx-odc-by': 'Open Data Commons Attribution License (ODC-BY)',
    'hdx-pddl': 'Open Data Commons Public Domain Dedication and License (PDDL)',
    'other-pd-nr': 'Public Domain / No Restrictions'
}


def get_date_from_concat_str(_str):
    result = ''

    if _str:
        res_list = []
        dates_list = str(_str).replace('[', '').replace(']', '').replace(' ', '').split('TO')
        for date in dates_list:
            if '*' not in date:
                _date = datetime.datetime.strptime(date.split('T')[0], '%Y-%m-%d')
                res_list.append(_date.strftime('%B %d, %Y'))
            else:
                res_list.append(date)
        result = ' to '.join(res_list)

    return result


def get_frequency_by_value(value):
    return UPDATE_FREQ_DICT.get(value, value)


def get_license_name_by_value(value):
    return LICENSES_DICT.get(value, value)
