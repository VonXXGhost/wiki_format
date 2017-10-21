from anime_staff import *

testanime = AnimeStaff('title')
testanime.add_episode('ep1', 'sub1')
testanime['ep1'].add_staff('pos1', 'name1')
testanime.save()
testanime['ep1'].add_staff('pos1', 'name2')
testanime.save()

persons= Persons()
persons.add_person('name')
persons['name'].add_position('title', 'ep', 'pos')
persons['name'].save()
persons['name'].add_position('title2', 'ep', 'pos')
persons['name'].save()