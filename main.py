from collections import defaultdict

import requests

import re

URL_NEUTER = 'https://lpsn.dsmz.de/text/genus-names-of-latin-origin-neuter-gender'
URL_FEMININE = 'https://lpsn.dsmz.de/text/genus-names-of-latin-origin-feminine-gender'
URL_MASCULINE = 'https://lpsn.dsmz.de/text/genus-names-of-latin-origin-masculine-gender'

RE_NAME = re.compile(r'<button id=".+?" class="accordion">(.+?)<a .+?<\/button>.+?<div class="panel">(.+?)<\/div>')
RE_INNER_HTML = re.compile(r'<a href=.+?>(.+?)<\/a>')


def parse_url(url, file_prefix):
    print(f'\nLoading: {url}')

    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        raise Exception(f'Error loading: {url}')
    text = r.text.replace('\n', '').replace('\r', '')

    re_names = RE_NAME.findall(text)
    if re_names[0][0].strip() == 'General remarks':
        re_names = re_names[1:]
    print(f'    - Found {len(re_names):,} names')

    out = defaultdict(list)
    for name, inner_html in re_names:
        name = name.strip()
        print(f'    - {name}')

        name_hits = RE_INNER_HTML.findall(inner_html)
        if len(name_hits) == 0:
            raise Exception(f'Error parsing name: {name}')

        for name_hit in name_hits:
            name_hit = name_hit.replace('<I>', '').replace('</I>', '').strip()
            print(f'        - {name_hit}')
            out[name].append(name_hit)

    print(f'Writing output files...')
    with open(f'{file_prefix}_all.tsv', 'w') as f_all, \
            open(f'{file_prefix}_unq.tsv', 'w') as f_unq, \
            open(f'{file_prefix}_count.tsv', 'w') as f_count, \
            open(f'{file_prefix}_count_unq.tsv', 'w') as f_count_unq, \
            open(f'{file_prefix}_word_cloud.txt', 'w') as f_word_cloud, \
            open(f'{file_prefix}_word_cloud_unq.txt', 'w') as f_word_cloud_unq:
        for name, list_names in out.items():

            # All names
            for set_name in list_names:
                f_all.write(f'{name}\t{set_name}\n')

            all_names_list = '\n'.join([name for _ in range(len(list_names))])
            f_word_cloud.write(f'{all_names_list}\n')

            # All names count
            f_count.write(f'{name}\t{len(list_names)}\n')

            # Unique names
            unq_names = set()
            for set_name in set(list_names):
                if (set_name.startswith('"') and set_name.endswith('"')) or (
                        set_name.startswith('[') and set_name.endswith(']')):
                    set_name = set_name[1:-1]
                unq_names.add(set_name)
            for unq_name in sorted(unq_names):
                f_unq.write(f'{name}\t{unq_name}\n')

            # Unique name count
            f_count_unq.write(f'{name}\t{len(unq_names)}\n')
            unq_names_list = '\n'.join([name for _ in range(len(unq_names))])
            f_word_cloud_unq.write(f'{unq_names_list}\n')
    return


def main():
    parse_url(URL_NEUTER, 'neuter')
    parse_url(URL_MASCULINE, 'masculine')
    parse_url(URL_FEMININE, 'feminine')


if __name__ == '__main__':
    main()
