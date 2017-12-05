#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Parse the credit to resume file from seesaawiki.jp

Usage:
    seesaawiki_format -s <URL>
    seesaawiki_format -a [-n] [<names>...]

Options:
    -h --help   show this
    -s      单网页解析模式
    -a      多网页解析模式
    -n      指定输出名字，不使用代表全部保存

'''

import seesaawiki
from docopt import docopt


def input_model():
    print('每行输入一个网址，当为非seesaawiki网址时自动结束\n')
    urls = []
    while True:
        url = input()
        if 'seesaawiki' not in url:
            print('输入结束')
            return urls
        urls.append(url)


if __name__ == '__main__':
    arguments = docopt(__doc__)
    if arguments['-s']:
        seesaawiki.page_parse(arguments['<URL>'])
        exit(0)
    elif arguments['-a']:
        urls = input_model()
        seesaawiki.pages_parse(urls, save_names=arguments['<names>'])