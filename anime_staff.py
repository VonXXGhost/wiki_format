import logging
from collections import defaultdict
import os

# log setting
LOG_FORMAT = '%(asctime)s | [%(levelname)s]%(filename)s[line:%(lineno)d][%(funcName)s]: %(message)s'
# logging.basicConfig(level=logging.INFO,
#                     format=LOG_FORMAT,
#                     datefmt='%d %b %Y %H:%M:%S',
#                     filename='anime_staff.log',
#                     )
# console = logging.StreamHandler()
# console.setLevel(logging.INFO)
# formatter = logging.Formatter(LOG_FORMAT)
# console.setFormatter(formatter)
# logging.getLogger('anime_staff').addHandler(console)
# logger = logging.getLogger('anime_staff')
logger = logging.getLogger('anime_staff')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('anime_staff.log', encoding='utf-8')
handler.setFormatter = logging.Formatter(LOG_FORMAT, datefmt='%d %b %Y %H:%M:%S')
logger.addHandler(handler)


class AnimeStaff:
    def __init__(self, title):
        self.episode = defaultdict(lambda: None)  # 指向EpisodeStaff对象
        self.title = title

    def __getitem__(self, item):
        return self.episode[item]

    def add_episode(self, episode, subtitle):
        ep_staff = EpisodeStaff(subtitle, episode)
        self.episode[episode] = ep_staff
        logger.info('<{}>-章节 {} 已添加'.format(self.title, episode))

    def save(self):
        path = os.path.join('.', 'animes')
        if not os.path.exists(path):
            os.mkdir(path)
        filename = self.title + '.txt'
        for x in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:  # 排除windows非法字符
            filename = filename.replace(x, '')
        filepath = os.path.join(path, filename)
        with open(filepath, 'a', encoding='utf-8') as file:
            content = '■ {}'.format(self.title) + '\n'
            for episode, ep_staffs in self.episode.items():
                content += ep_staffs.text()
            content += '\n'
            file.write(content)
        logger.info('<{}>信息已保存'.format(self.title))


class EpisodeStaff:
    def __init__(self, subtitle, episode):
        self.subtitle = subtitle
        self.episode = episode
        self.staffs = defaultdict(set)  # 如['脚本']→set对象

    def add_staff(self, position, name):
        self.staffs[position].add(name)

    def text(self):
        txt = '{} {}:\n'.format(self.episode, self.subtitle)
        for position, staffs in self.staffs.items():
            txt += '·{}: '.format(position)
            for name in staffs:
                txt += name + '、'
            txt = txt[:-1]
            txt += '\n'
        return txt


class PersonResume:
    def __init__(self, name):
        self.positions = defaultdict(lambda: defaultdict(list))  # ['title']['position']→episodes
        self.name = name

    def add_position(self, title, episode, position):
        if episode in self.positions[title][position]:
            logger.warning('"{0}":[{1}][{2}]-[{3}]已存在'.format(self.name, title, position, episode))
            return False
        self.positions[title][position].append(episode)
        logger.info('"{0}":[{1}][{2}]-[{3}]已添加'.format(self.name, title, position, episode))
        return True

    def text(self):
        content = ''
        for title, positions in self.positions.items():
            content += '■ {}'.format(title) + '\n\t'
            for position, episodes in self.positions[title].items():
                if len(episodes) == 1 and episodes[0] == '':
                    content += '· {}'.format(position)
                else:
                    content += '· {}: '.format(position)
                flag = True
                for episode in episodes:
                    if flag:
                        content += episode
                        flag = False
                    else:
                        content += '、' + episode
                content += '\n\t'
            content += '\n'
        return content

    def save(self):
        path = os.path.join('.', 'resumes')
        if not os.path.exists(path):
            os.mkdir(path)
        filename = self.name + '.txt'
        filepath = os.path.join(path, filename)
        with open(filepath, 'a', encoding='utf-8') as file:
            logger.debug(self.text())
            file.write(self.text())
        logger.info('“{}”保存完成'.format(self.name))


class Persons:
    def __init__(self):
        self.who = defaultdict(lambda: None)  # ['name']：PersonResume对象

    def __getitem__(self, item):
        if self.who[item] is None:
            self.add_person(item)
        return self.who[item]

    def __setitem__(self, key, value):
        self.who[key] = value

    def add_person(self, name):
        if self.who[name] is not None:
            logger.warning('"{}"已存在'.format(name))
            return False

        resume = PersonResume(name)
        self[name] = resume
        # logger.info('"{}"映射已建立'.format(name))
        return True

    def del_person(self, name):
        # 注：不检查键是否存在
        self[name] = None
        logger.info('"{}"映射已删除'.format(name))

    def save_as_one_file(self, filename='persons'):
        path = os.path.join('.', 'persons')
        if not os.path.exists(path):
            os.mkdir(path)
        filename = filename + '.txt'
        filepath = os.path.join(path, filename)
        with open(filepath, 'a', encoding='utf-8') as file:
            for name, resume in self.who.items():
                content = '● {}：\n'.format(name)
                content += resume.text() + '\n'
                file.write(content)
        logger.info('已保存全员信息为单文件')
