import datetime
import re

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
    'cc-by-sa': 'Creative Commons Attribution Share-Alike',
    'cc-nc': 'Creative Commons Non-Commercial (Any)',
    'cc-zero': 'Creative Commons CCZero',
    'gfdl': 'GNU Free Documentation License',
    'hdx-multi': 'Multiple Licenses',
    'hdx-odc-by': 'Open Data Commons Attribution License (ODC-BY)',
    'hdx-odc-odbl': 'Open Database License (ODC-ODbL)',
    'hdx-other': 'Other',
    'hdx-pddl': 'Open Data Commons Public Domain Dedication and License (PDDL)',
    'notspecified': 'License not specified',
    'odc-by': 'Open Data Commons Attribution License',
    'odc-odbl': 'Open Data Commons Open Database License (ODbL)',
    'odc-pddl': 'Open Data Commons Public Domain Dedication and License (PDDL)',
    'other-at': 'Other (Attribution)',
    'other-closed': 'Other (Not Open)',
    'other-nc': 'Other (Non-Commercial)',
    'other-open': 'Other (Open)',
    'other-pd': 'Other (Public Domain)',
    'other-pd-nr': 'Public Domain / No Restrictions',
    'uk-ogl': 'UK Open Government Licence (OGL)'
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


def remove_markdown(markdown_text):
    # Remove headers (lines starting with '#')
    markdown_text = re.sub(r'^#+\s+', '', markdown_text, flags=re.MULTILINE)

    # Remove emphasis (e.g., '*italic*', '**bold**')
    markdown_text = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', markdown_text)

    # Remove code blocks (e.g., ```python ... ```)
    markdown_text = re.sub(r'```[^`]+```', '', markdown_text)

    # Remove inline code (e.g., `code`)
    markdown_text = re.sub(r'`([^`]+)`', r'\1', markdown_text)

    # Remove links (e.g., [text](url))
    markdown_text = re.sub(r'\[([^]]+)\]\([^)]+\)', r'\1', markdown_text)

    # Remove images (e.g., ![alt text](url))
    markdown_text = re.sub(r'!\[([^\]]+)\]\([^)]+\)', r'\1', markdown_text)

    # Remove lists (e.g., - item)
    markdown_text = re.sub(r'^\s*[-*]\s+', '', markdown_text, flags=re.MULTILINE)

    # Remove blockquotes (e.g., > quote)
    markdown_text = re.sub(r'^>\s+', '', markdown_text, flags=re.MULTILINE)

    # Remove horizontal rules (e.g., ---)
    markdown_text = re.sub(r'^[-*_]{3,}\s*$', '', markdown_text, flags=re.MULTILINE)

    return markdown_text
