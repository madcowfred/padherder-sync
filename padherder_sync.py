#!/usr/bin/env python

"""
Simple script to sync JSON box data to the PADherder API. It seems to work using
some test data provided to me, I would really recommend backing up your data first
though.
"""

__author__ = 'Freddie (freddie@padherder.com)'
__version__ = '0.1.1'

import cPickle
import json
import os
import requests
import sys
import time

from urlparse import urljoin

# ---------------------------------------------------------------------------
# Don't change anything below here unless you know what you're doing
#API_ENDPOINT = 'http://192.168.1.254:8001/user-api'

# temporary workaround until I can work out what in the hell is going on with the OpenSSL error
if os.name == 'nt':
    API_ENDPOINT = 'http://www.padherder.com/user-api'
    URL_MONSTER_DATA = 'http://www.padherder.com/api/monsters/'
else:
    API_ENDPOINT = 'https://www.padherder.com/user-api'
    URL_MONSTER_DATA = 'https://www.padherder.com/api/monsters/'

URL_USER_DETAILS = '%s/user/%%s/' % (API_ENDPOINT)
URL_MONSTER_CREATE = '%s/monster/' % (API_ENDPOINT)

# Remap US monster IDs to PADherder/Wiki IDs
ID_REMAP = {
    669: 924,
    670: 925,
    671: 926,
    672: 927,
    673: 928,
    674: 929,
    675: 930,
    676: 931,
    677: 932,
    678: 933,
    679: 934,
    680: 935,
    924: 1924,
    925: 1925,
    926: 1926,
    927: 1927,
    928: 1928,
    929: 1929,
    930: 1930,
    931: 1931,
    932: 1932,
}

# Horrifying XP tables, woo
XP_TABLES = {
    1000000: [0, 11, 59, 164, 337, 588, 927, 1364, 1904, 2556, 3326, 4221, 5247, 6409, 7714, 9166, 10770, 12533, 14458, 16551, 18815, 21256, 23878, 26684, 29680, 32869, 36255, 39842, 43634, 47635, 51849, 56278, 60927, 65799, 70898, 76226, 81788, 87587, 93625, 99907, 106435, 113213, 120243, 127528, 135072, 142878, 150949, 159287, 167895, 176777, 185934, 195371, 205089, 215092, 225382, 235962, 246834, 258001, 269467, 281232, 293301, 305675, 318357, 331349, 344655, 358276, 372216, 386475, 401058, 415966, 431201, 446767, 462664, 478897, 495466, 512375, 529625, 547220, 565160, 583449, 602088, 621080, 640427, 660131, 680194, 700619, 721408, 742562, 764085, 785977, 808241, 830880, 853895, 877288, 901062, 925217, 949758, 974685, 1000000],
    1500000: [0, 16, 89, 246, 505, 882, 1391, 2045, 2856, 3834, 4989, 6332, 7870, 9614, 11570, 13748, 16156, 18800, 21687, 24826, 28223, 31884, 35816, 40026, 44520, 49303, 54383, 59763, 65452, 71453, 77773, 84417, 91390, 98699, 106347, 114339, 122682, 131380, 140438, 149861, 159653, 169819, 180364, 191292, 202609, 214317, 226423, 238930, 251843, 265165, 278902, 293057, 307634, 322638, 338073, 353943, 370251, 387002, 404200, 421848, 439951, 458512, 477535, 497024, 516983, 537415, 558323, 579713, 601587, 623949, 646802, 670150, 693997, 718345, 743199, 768563, 794438, 820829, 847740, 875173, 903132, 931620, 960640, 990196, 1020292, 1050929, 1082112, 1113844, 1146127, 1178965, 1212362, 1246320, 1280842, 1315932, 1351592, 1387826, 1424637, 1462027, 1500000],
    2000000: [0, 21, 119, 328, 673, 1176, 1855, 2727, 3808, 5112, 6652, 8442, 10493, 12818, 15427, 18331, 21541, 25066, 28917, 33102, 37630, 42512, 47755, 53368, 59360, 65738, 72510, 79685, 87269, 95271, 103697, 112556, 121854, 131598, 141795, 152453, 163577, 175174, 187251, 199814, 212870, 226425, 240485, 255056, 270145, 285756, 301897, 318573, 335790, 353553, 371869, 390742, 410179, 430184, 450764, 471923, 493668, 516003, 538933, 562464, 586601, 611349, 636713, 662699, 689310, 716553, 744431, 772951, 802116, 831931, 862402, 893533, 925329, 957794, 990933, 1024750, 1059251, 1094439, 1130320, 1166897, 1204175, 1242159, 1280853, 1320262, 1360389, 1401239, 1442816, 1485125, 1528169, 1571954, 1616483, 1661760, 1707790, 1754576, 1802123, 1850435, 1899516, 1949369, 2000000],
    2500000: [0, 26, 149, 410, 841, 1470, 2319, 3409, 4760, 6390, 8315, 10553, 13117, 16023, 19284, 22914, 26926, 31333, 36146, 41377, 47038, 53140, 59694, 66711, 74200, 82172, 90638, 99606, 109086, 119088, 129622, 140695, 152317, 164498, 177244, 190566, 204471, 218967, 234064, 249768, 266088, 283031, 300606, 318820, 337681, 357196, 377372, 398217, 419738, 441942, 464836, 488428, 512723, 537730, 563455, 589904, 617085, 645003, 673666, 703080, 733251, 764187, 795892, 828373, 861638, 895691, 930539, 966188, 1002645, 1039914, 1078003, 1116916, 1156661, 1197242, 1238666, 1280938, 1324063, 1368049, 1412900, 1458621, 1505219, 1552699, 1601067, 1650327, 1700486, 1751548, 1803520, 1856406, 1910212, 1964942, 2020603, 2077200, 2134737, 2193220, 2252654, 2313044, 2374395, 2436712, 2500000],
    3000000: [0, 32, 178, 492, 1010, 1764, 2782, 4091, 5712, 7668, 9978, 12663, 15740, 19227, 23141, 27497, 32311, 37599, 43375, 49652, 56446, 63768, 71633, 80053, 89040, 98607, 108765, 119527, 130903, 142906, 155546, 168834, 182781, 197397, 212693, 228679, 245365, 262761, 280876, 299721, 319305, 339638, 360728, 382584, 405217, 428635, 452846, 477860, 503685, 530330, 557803, 586113, 615268, 645276, 676146, 707885, 740502, 774004, 808400, 843696, 879902, 917024, 955070, 994048, 1033965, 1074829, 1116647, 1159426, 1203174, 1247897, 1293603, 1340300, 1387993, 1436690, 1486399, 1537125, 1588876, 1641659, 1695480, 1750346, 1806263, 1863239, 1921280, 1980393, 2040583, 2101858, 2164224, 2227687, 2292254, 2357931, 2424724, 2492640, 2561684, 2631864, 2703185, 2775652, 2849274, 2924054, 3000000],
    4000000: [0, 42, 238, 656, 1346, 2352, 3710, 5454, 7616, 10224, 13304, 16884, 20987, 25636, 30854, 36663, 43082, 50132, 57833, 66203, 75261, 85024, 95511, 106737, 118720, 131475, 145020, 159369, 174538, 190542, 207395, 225112, 243708, 263196, 283591, 304905, 327153, 350348, 374502, 399628, 425740, 452850, 480970, 510112, 540289, 571513, 603795, 637147, 671580, 707107, 743738, 781484, 820358, 860368, 901528, 943847, 987336, 1032005, 1077866, 1124928, 1173202, 1222699, 1273427, 1325398, 1378621, 1433106, 1488863, 1545901, 1604232, 1663863, 1724805, 1787066, 1850657, 1915587, 1981865, 2049500, 2118502, 2188878, 2260639, 2333794, 2408351, 2484319, 2561707, 2640523, 2720777, 2802477, 2885632, 2970250, 3056339, 3143908, 3232966, 3323520, 3415579, 3509152, 3604246, 3700870, 3799031, 3898739, 4000000],
    5000000: [0, 53, 297, 820, 1683, 2940, 4637, 6818, 9520, 12779, 16630, 21105, 26234, 32045, 38568, 45828, 53852, 62665, 72291, 82754, 94076, 106280, 119388, 133421, 148400, 164344, 181275, 199211, 218172, 238177, 259244, 281390, 304635, 328995, 354488, 381132, 408941, 437934, 468127, 499535, 532175, 566063, 601213, 637641, 675362, 714391, 754744, 796433, 839475, 883883, 929672, 976855, 1025447, 1075461, 1126910, 1179809, 1234170, 1290007, 1347333, 1406160, 1466503, 1528373, 1591784, 1656747, 1723276, 1791382, 1861078, 1932377, 2005290, 2079829, 2156006, 2233833, 2313322, 2394484, 2477331, 2561875, 2648127, 2736098, 2825799, 2917243, 3010439, 3105399, 3202134, 3300654, 3400972, 3503097, 3607040, 3712812, 3820423, 3929885, 4041207, 4154400, 4269474, 4386440, 4505308, 4626087, 4748789, 4873423, 5000000],
}

# ---------------------------------------------------------------------------
# Request headers
headers = {
    'accept': 'application/json',
    'user-agent': 'padherder-sync %s' % (__version__),
}

# ---------------------------------------------------------------------------

def we_are_frozen():
    """Returns whether we are frozen via py2exe.
    This will affect how we find out where we are located."""

    return hasattr(sys, "frozen")

def module_path():
    """ This will get us the program's directory,
    even if we are frozen using py2exe"""

    if we_are_frozen():
        return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding()))

    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding()))

# ---------------------------------------------------------------------------

def xp_at_level(xp_curve, level):
    curve = XP_TABLES.get(xp_curve)
    if level > len(curve) - 1:
        return curve[-1]
    else:
        return curve[level - 1]

def main():
    # Requests session so we get HTTP Keep-Alive
    session = requests.Session()
    session.auth = (sys.argv[2], sys.argv[3])
    session.headers = headers
    # Limit the session to a single concurrent connection
    session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=1))
    session.mount('https://', requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=1))

    # Check for monster cache (8 hours)
    cache_old = time.time() - (8 * 60 * 60)
    pickle_path = os.path.join(module_path(), 'monster_data.pickle')
    if os.path.exists(pickle_path) and os.stat(pickle_path).st_mtime > cache_old:
        # Use cached data
        print 'Using cached monster data.'
        monster_data = cPickle.load(open(pickle_path, 'rb'))

    else:
        # Retrieve monster API data
        print 'Retrieving monster data from PADherder API...',
        sys.stdout.flush()

        r = session.get(URL_MONSTER_DATA)
        if r.status_code != requests.codes.ok:
            print 'failed: %s' % (r.status_code)
            return
        print 'done.'

        # Build monster data map
        monster_data = {}
        for monster in json.loads(r.content):
            monster_data[monster['id']] = monster

        # Cache it
        cPickle.dump(monster_data, open(pickle_path, 'wb'))

    # Retrieve the user's monster data
    print 'Retrieving user data from PADherder API...',
    sys.stdout.flush()

    url = URL_USER_DETAILS % (session.auth[0])
    r = session.get(url)
    if r.status_code != requests.codes.ok:
        print 'failed: %s %s' % (r.status_code, r.content)
        return

    user_data = json.loads(r.content)
    print 'done.'

    # Build a map of monsterID:materials
    material_map = {}
    for material in user_data['materials']:
        material_map[material['monster']] = material

    # Build a map of monsterID:monsters, (+id, -current_xp, -current_skill, -current_awakening, -plus_hp ,-plus_atk, -plus_rcv) order
    monster_map = {}
    for monster in user_data['monsters']:
        monster_map.setdefault(monster['monster'], []).append(monster)

    # Load the captured data
    data = json.loads(open(sys.argv[1], 'rb').read())

    # Sort the capture data the same way as the user monster data
    temp = []
    for card in data['card']:
        card['no'] = ID_REMAP.get(card['no'], card['no'])
        monster = monster_data[card['no']]

        # Cap card XP to monster's max XP
        card['exp'] = min(card['exp'], xp_at_level(monster['xp_curve'], monster['max_level']))
        # Cap card awakening to monster's max awoken level
        card['plus'][3] = min(card['plus'][3], len(monster['awoken_skills']))

        temp.append([
            card['no'],
            -card['exp'],
            -card['slv'],
            -card['plus'][3],
            -card['plus'][0],
            -card['plus'][1],
            -card['plus'][2],
            card,
        ])

    temp.sort()
    data['card'] = [t[-1] for t in temp]

    # Iterate over the cards doing stuff
    material_counts = {}
    for card in data['card']:
        monster_id = card['no']

        # Update material counts
        if monster_id in material_map:
            material_counts[monster_id] = material_counts.get(monster_id, 0) + 1

        # Skip - 0=Evo, 12=Awoken, 14=Enhance
        if monster_data[monster_id]['type'] in (0, 12, 14):
            continue

        # Check for existing monsters
        found = False
        monsters = monster_map.get(monster_id, [])
        for i, monster in enumerate(monsters):
            if card['exp'] >= monster['current_xp'] or card['slv'] >= monster['current_skill'] or card['plus'][0] >= monster['plus_hp'] or \
                card['plus'][1] >= monster['plus_atk'] or card['plus'][2] >= monster['plus_rcv'] or card['plus'][3] >= monster['current_awakening']:

                monsters.pop(i)
                found = True
                data = {}

                # update changed data only
                if card['exp'] > monster['current_xp']:
                    data['current_xp'] = card['exp']

                if card['slv'] > monster['current_skill']:
                    data['current_skill'] = card['slv']

                if card['plus'][0] > monster['plus_hp']:
                    data['plus_hp'] = card['plus'][0]

                if card['plus'][1] > monster['plus_atk']:
                    data['plus_atk'] = card['plus'][1]

                if card['plus'][2] > monster['plus_rcv']:
                    data['plus_rcv'] = card['plus'][2]

                if card['plus'][3] > monster['current_awakening']:
                    data['current_awakening'] = card['plus'][3]

                # If any fields need updating, do so
                if len(data) > 0:
                    data['monster'] = monster_id
                    r = session.patch(monster['url'], data)
                    if r.status_code == requests.codes.ok:
                        print 'Updated monster #%d: %s' % (monster['id'], ', '.join(k for k in data.keys() if k != 'monster'))
                    else:
                        print 'Failed updating monster #%d: %s %s' % (monster['id'], r.status_code, r.content)

                break

        # Monster not found, create a new one
        if not found:
            data = dict(
                monster=monster_id,
                current_xp=card['exp'],
                current_skill=card['slv'],
                plus_hp=card['plus'][0],
                plus_atk=card['plus'][1],
                plus_rcv=card['plus'][2],
                current_awakening=card['plus'][3],
            )

            r = session.post(URL_MONSTER_CREATE, data)
            if r.status_code == requests.codes.ok or r.status_code == 201:
                print 'Created monster %r (Level %d; Skill %d; Plus %d/%d/%d; Awoken %d)' % (monster_data[monster_id]['name'], card['lv'],
                    card['slv'], card['plus'][0], card['plus'][1], card['plus'][2], card['plus'][3])
            else:
                print 'Failed creating monster %r: %s %s' %(monster_data[monster_id]['name'], r.status_code, r.content)

    # Maybe update materials
    for monster_id, material in material_map.items():
        new_count = material_counts.get(monster_id, 0)
        if new_count != material['count']:
            data = dict(count=new_count)
            r = session.patch(material['url'], data)
            if r.status_code == requests.codes.ok or r.status_code == 201:
                print 'Updated material %r from %d to %d' % (monster_data[monster_id]['name'], material['count'], new_count)
            else:
                print 'Failed updating material %r: %s %s' % (monster_data[monster_id]['name'], r.status_code, r.content)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        if we_are_frozen():
            print 'USAGE: padherder_sync.exe [capture file] [PADherder username] [PADherder password]'
        else:
            print 'USAGE: padherder_sync.py [capture file] [PADherder username] [PADherder password]'
        sys.exit(1)

    main()
