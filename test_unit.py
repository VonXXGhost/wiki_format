#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from anime_staff import *


class TestPersons(unittest.TestCase):
    def test_data(self):
        resume = PersonResume('test')
        self.assertIsInstance(resume.positions['test']['position'], list)

    def test_add_position(self):
        resume = PersonResume('test')
        resume.add_position('t1', 'e1', 'pos1')
        self.assertEqual(resume.positions['t1']['pos1'], list(['e1']))
        resume.add_position('t1', 'e2', 'pos1')
        self.assertEqual(resume.positions['t1']['pos1'], list(['e1', 'e2']))
        self.assertEqual(len(resume.positions['t1']['pos2']), 0)
        self.assertTrue(resume.add_position('t1', 'e3', 'pos1'))
        self.assertFalse(resume.add_position('t1', 'e1', 'pos1'))

    def test_add_persons(self):
        persons = Persons()
        persons.add_person('test')
        persons['test'].add_position('t1', 'e1', 'pos1')
        self.assertEqual(persons['test'].positions['t1']['pos1'], list(['e1']))
        self.assertIs(persons['none'], None)


class TestAnimeStaffs(unittest.TestCase):
    def test_EpisodeStaff(self):
        ep_s = EpisodeStaff('sub', 'ep')
        ep_s.add_staff('pos1', 'name1')
        ep_s.add_staff('pos1', 'name2')
        ep_s.add_staff('pos2', 'name1')
        self.assertEqual(ep_s.staffs['pos1'], {'name1', 'name2'})

        def ep_s_equal():
            res = ['ep sub:\n·pos1: name2、name1\n·pos2: name1\n',
                   'ep sub:\n·pos1: name1、name2\n·pos2: name1\n',
                   'ep sub:\n·pos2: name1\n·pos1: name1、name2\n',
                   'ep sub:\n·pos2: name1\n·pos1: name2、name1\n']
            text = ep_s.text()
            for x in res:
                if x == text:
                    return True
            return False

        self.assertTrue(ep_s_equal())


if __name__ == '__main__':
    unittest.main()
