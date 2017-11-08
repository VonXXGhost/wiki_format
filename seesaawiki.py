#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from anime_staff import *
from collections import deque
import requests
import re

re_position = re.compile(r'(?P<positions>.+)[：:](?P<names>.*)')


class ParseEnd(Exception):
    pass


def get_title_content_of(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    try:  # 去除概括表格
        table = soup.table
        table.previous_sibling.decompose()
        table.decompose()
    except:
        pass
    title = str(next(soup.select('#page-header-inner > div.title > div > h2')[0].strings)).strip()
    content = soup.select('#page-body-inner > div.user-area')[0]
    return title, content


def position_list(positions):
    if positions is None or positions == '':
        return []
    return re.split('[・·/／]', positions)


def name_list(names):
    if names is None or names == '':
        return []
    return re.split(r'[／→、　\n](?![^（）]*）)', names)  # 带括号


def get_positions_names_of(element):
    e_re = re.search(re_position, element)
    if e_re is not None:
        positions = e_re.group('positions').strip()
        names = e_re.group('names').strip()
    else:
        positions = None
        names = element
    return position_list(positions), name_list(names)


def add_person_by_queues(persons, pos_que, name_que, info):
    while len(name_que) > 0:
        name = name_que.popleft()
        if '（' in name:  # 注释判定
            try:
                name, remarks = re.search('(.+)（(.*)）', name).group(1, 2)
            except:
                name = re.search('(.*)（(.*)', name).group(1)
                remarks = ''
            if name == '':
                continue

            if '話' in remarks:
                info['ep'] = remarks
        else:
            name = re.split(r'[\[*]', name)[0]
            if 'ep' not in info:
                info['ep'] = 'unknown'
        name = name.strip()
        for position in pos_que:
            persons[name].add_position(info['title'], info['ep'], position)


def element_parse(element, persons, pos_que, name_que, info):
    if element.name == 'hr':
        add_person_by_queues(persons, pos_que, name_que, info)
        pos_que.clear()
        raise ParseEnd
    if element.name == 'br':
        return
    try:
        if '©' in element.get_text():
            return
    except:
        if '©' in str(element):
            return

    try:
        element = element.get_text().strip()
    except AttributeError:
        element = str(element).strip()
    positions, names = get_positions_names_of(element)
    if len(positions) == 0:
        name_que.extend(names)
    else:
        add_person_by_queues(persons, pos_que, name_que, info)
        pos_que.clear()
        pos_que.extend(positions)
        name_que.extend(names)


def mainstaff_parse_span(first, persons, info):
    pos_que = deque()
    name_que = deque()
    info['ep'] = ''
    element_parse(first, persons, pos_que, name_que, info)
    for element in first.next_siblings:
        try:
            element_parse(element, persons, pos_que, name_que, info)
        except ParseEnd:
            break


def mainstaff_parse_div(first, persons, info):
    pos_que = deque()
    name_que = deque()
    positions, names = get_positions_names_of(first)
    pos_que.extend(positions)
    name_que.extend(names)
    for element in first.next_elements:
        info['ep'] = ''
        try:
            element_parse(element, persons, pos_que, name_que, info)
        except ParseEnd:
            break


def mainstaff_parse(first, persons, info):
    if first.parent.name == 'span':
        mainstaff_parse_span(first.parent, persons, info)
    elif first.parent.name == 'div':
        mainstaff_parse_div(first, persons, info)
    else:
        logger.error('未知的main staff html格式')
        raise RuntimeError('未知的main staff html格式')
    pass


def OPED_parse(boundary, persons, info):
    pos_que = deque()
    name_que = deque()
    OP_count = 0
    ED_count = 0

    for element in boundary.next_siblings:
        if element.name != 'b' and element.name != 'br':
            try:
                element_parse(element, persons, pos_que, name_que, info)
            except ParseEnd:
                break
        elif element.name == 'b':
            black = element.get_text()
            if re.search('(OP|オープニングアニメーション)', black):
                OP_count += 1
                if OP_count > 1:
                    info['ep'] = 'OP' + str(OP_count)
                else:
                    info['ep'] = 'OP'
            elif re.search('(ED|エンディングアニメーション)', black):
                ED_count += 1
                if ED_count > 1:
                    info['ep'] = 'ED' + str(ED_count)
                else:
                    info['ep'] = 'ED'
            else:
                print('Warring b tag in OPED')
                logger.warning('Warring b tag in OPED')
                element_parse(element, persons, pos_que, name_que, info)
        elif element.name == 'br':
            continue
        else:
            print('unknown situation')


def general_parse(boundary, persons, info):
    pos_que = deque()
    name_que = deque()
    # 获取章节
    block_first = boundary.find_next('span', text=re_position)
    if block_first is None:
        print('block_first is None，章节获取失败，可能是空章节='.format())
        logger.error('block_first is None，章节获取失败，可能是空章节')
        return
    if re.search('\d+話', block_first.get_text()):
        block_first = block_first.find_next('span', text=re_position)
    ep_info = ''
    for element in boundary.next_siblings:
        if element != block_first:
            try:
                ep_info += element.get_text()
            except AttributeError:
                ep_info += str(element)
        else:
            break
    try:
        info['ep'] = re.findall('\d+', ep_info)[0]
    except:
        print('章节获取失败，可能是空章节:\n{}'.format(ep_info.strip()))
        logger.error('章节获取失败，可能是空章节:\n{}'.format(ep_info.strip()))
        return

    element_parse(block_first, persons, pos_que, name_que, info)
    for element in block_first.next_siblings:
        try:
            element_parse(element, persons, pos_que, name_que, info)
        except ParseEnd:
            break


def content_parse(content, info):
    persons = Persons()
    first = content.find(text=re_position)
    mainstaff_parse(first, persons, info)
    for boundary in content.find_all('hr'):
        block_first = boundary.find_next(text=re_position)
        if block_first == first:
            continue
        black = ''
        for element in boundary.next_siblings:
            if element.name == 'b':
                black += element.get_text()
            if element.name == 'span':
                break

        if re.search('(OP|ED|オープニングアニメーション|エンディングアニメーション)', black):
            OPED_parse(boundary, persons, info)
        elif 'テーマ' in black:
            continue
        elif 'スタッフクレジット' in black:
            mainstaff_parse(block_first, persons, info)
        else:
            general_parse(boundary, persons, info)

    title = info['title']
    for x in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
        title = title.replace(x, '')
    persons.save_as_one_file(filename=title)
