"""Regression test for the Qing 1919-1935 (qing_interwar) focus tree.

Two properties are guarded, and both matter:

  * identity and non-layout content -- every focus id from the 99-focus chapter is
    still present, and each focus body is byte-identical to the baseline once only
    its own x/y value lines are removed. This is what makes a layout pass provably
    gameplay-neutral: a reward, prerequisite, icon, cost, ai_will_do, search-filter,
    availability, allow_branch or localisation-key edit changes the digest.
  * layout validity -- no two focuses share a cell, same-row pairs keep the engine's
    two-cell clearance, every prerequisite sits on a row above its child, coordinates
    stay inside the declared grid, no prerequisite connector crosses another
    unrelated connector, and the chapter keeps at most four long connectors.

Individual coordinates are intentionally NOT pinned: a future layout pass may move
any focus as long as both properties hold. The negative control at the end proves the
checks can fail, including on a reward edit, an icon swap and a prerequisite edit.
"""
import hashlib
import os
import re
import shutil
import tempfile

TREE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'common', 'national_focus', 'qing_interwar.txt')

FOCUS_COUNT = 99
MAX_X = 49
MAX_Y = 11
MAX_LONG_CONNECTORS = 4
MAX_CROSSINGS = 0

# sha256 of each focus body with only its x/y value lines removed, taken from the
# gameplay state the layout pass started from (git revision 75f78e153 working copy,
# 2026-10-27).
BASELINE = {
    'QW2_settlement_government':
        'e3f4498609245fae5b3cc29f2ac5c0cea4ccc74681e97745f60a9fba39c1c481',
    'QW2_constitutional_trunk':
        '9086bb37092cc4b878a287d5748f8fd5b038b0580f367357659dcd52967133b9',
    'QW2_constitutional_elections':
        '042382a4ed694df785c35ac8d589af9dedcba8a5409c0554e11ee7588c3bf86e',
    'QW2_constitutional_parties':
        '29d026e526110437a9b4b8a04369347a2985169fc2a8044093505d09394b19b0',
    'QW2_constitutional_cabinet':
        '1190454f677d44f36b1a3eafa90aa0643511f445173da30a9baea2edcec3fcc7',
    'QW2_constitutional_crisis':
        '46ba9e2bd8f8cfe2041e4e0801bf8edb83ee6f9e1d48d8b32ec5d5dc71874f78',
    'QW2_constitutional_capstone':
        '3fd50dfe4cb7e5418c73f9ea07930c947219b6a7b1dc816ab94dd7f5c3d477e5',
    'QW2_authoritarian_trunk':
        'e5d7d25fabc94ca110612d4d6b58309aae2b62d35b607507e245ab40ca8b8438',
    'QW2_authoritarian_provinces':
        'd3a4e58f2f7bb16ffcd770bd7e38f5e4afff9c182aa21ce6ad6e958827be9f12',
    'QW2_authoritarian_censorate':
        'a958c17f2bef9990535483dfe7d8f122da22a69f9379a57a2e9782d994e99327',
    'QW2_authoritarian_schools':
        'dc0ce33d799c079761e95ca469efe459f6e9a456bb3de83b2d7822cb152d426a',
    'QW2_authoritarian_opposition':
        'f23b15f04c0acde99047f0eb735834e69facd8fb6b5c539c916b79f6b815a33c',
    'QW2_authoritarian_capstone':
        '37b17a86bef058d69d6e23973c6ddeb12c0d293a564ad31623755c77671a353f',
    'QW2_yuan_trunk':
        '64a6c401c22dcc60b7e32e7c6e0795efdfa15832f31768a32d2a84f54766eeba',
    'QW2_yuan_army_state':
        '30062fecc34c14a0ff6200a832262cee397f398e74ea2104a24b17d9c9150abf',
    'QW2_yuan_finance':
        '949afde1eb93e8b783441b297a9b0889821f1d91a318417cfeb1ac0352f0aebe',
    'QW2_yuan_succession_crisis':
        'bcd7082ada7fa348d63dc29c65f941dce6cd97509a847d1e299e94d299aa3e0e',
    'QW2_yuan_capstone':
        'ccfaf687fd1c7e47cf639145dfefdf917755f6b53d2fcaf3558b1e759e3add5e',
    'QW2_federal_trunk':
        'ded322013aedc3d584839a6376819fcc41aa936cf84f0e44d48dd5dd3a1107b7',
    'QW2_federal_provinces':
        'dea3d2e3aaba71440a78ed32b96c13435acd271aa0e4638f9f737c0f6ffc86de',
    'QW2_federal_taxation':
        'b6ae7fd6c91da874955d352c2d300e3060d3510f004866bb9a7b99d3ff40f404',
    'QW2_federal_armies':
        '1f0b79d7a400d1f2ce79b29270680bd5c7f824e4f9395ebcc8cae5001d891044',
    'QW2_federal_compromise':
        '16d0e2a844d86957b3f026edd26e72961ef85545b6ac45df63e8fcb6720da2ff',
    'QW2_federal_capstone':
        'ad5face0c8bdd4e4907751a65be7c2cdc94818959a2b7d316b75bb5087eacc86',
    'QW2_industrial_takeoff':
        'cbd4641fef93eca02a9a61c6974a67eb3b2f42fb236d100efc2e76c825217bc4',
    'QW2_cotton_mills':
        '159dc73748adabd628cc83315c9d7750228c768a504c00173623382dddb5d84c',
    'QW2_coal_and_steel':
        '1695b227fb7a69b98be4ebf737d2d8bf29143d7411e6d9bdbd1dcec14ee8e381',
    'QW2_railway_expansion':
        'e227fb9c05624e50cd6c8ff3aacee5e3ce53fa2fa7fbf3d885efb03dbe55d7f1',
    'QW2_shanghai_port':
        '0f79292986b7cd79e8d82ca5405110125534421d030830dc17cf8ab796ae36d9',
    'QW2_education_drive':
        'b089f2960c4693af2c7c1c22c8d49632ccb56825e9d6ba5a772276e80cc6b5c8',
    'QW2_public_health':
        '929d1aeb90ba9bda1b8ac0c4ed536560916cfbea8e15f48d79cbc313c187f9b0',
    'QW2_land_reform':
        '000866967d014b547f6dcbd6601ac9860cb16bfb382107684e0eb88cfc9bab0e',
    'QW2_state_bank':
        'a9475fd1d79ec9f60894668b1d9b6fa222ca8e60b1bf1db5ac32e8334dd4d0c6',
    'QW2_heavy_industry':
        '362a43ec1295ec75ae800891a60b47aeaf333ef0d4a809d36b044d3080db1044',
    'QW2_economy_capstone':
        'c89a9fc17d682e239922b767665676087503b591e6d768d44629c68e82b7c6f5',
    'QW2_army_establishment':
        '5e748cad63b296b6f2b9dbd7439525ab5d20067d9727468d977af411e3290c0c',
    'QW2_army_air_force':
        '5a1ac82d920b1d2df9043544d2dc7419e3d8cb98836b782fda0099cf610135b1',
    'QW2_army_navy':
        '143eadca882e6d6f812221abd5a5afeb107e4f9eb45393881857ab7dfde00afa',
    'QW2_army_doctrine':
        'ef5b3fc7a02556f8e981d135d2bb6c90a9e067c594730d4d1be4dd7334392d1a',
    'QW2_army_academies':
        '1c004e18f2db337ba57728c761c08f5730ea1ff5c8cc6e14567c1ce64b47c351',
    'QW2_army_arsenals':
        '850d72e4b375a222018b2878acec75486cfe36b5a21591140e06504a2f96275e',
    'QW2_army_fortifications':
        'acab4693c84934b606ffc3a86be0eea4bf5f110288f0338f2cb417d9c12ded30',
    'QW2_army_capstone':
        '4791a71cf103e811651904c909ade2c42852fca83f83233be40796dff67787c7',
    'QW2_versailles_revision':
        'fa289e3077df8e279a5ae7207d19f2e897726b3d0e88d4530d24d4de53542286',
    'QW2_washington_system':
        'e348b3a9e40879a4b1e73b0b3cddf4d02a109089b8cc07f045e7237d41ded455',
    'QW2_soviet_relations':
        '5e620547e7708ec09f9d95acf568383a591847e0a9c1de238d8d6264d70df24b',
    'QW2_japanese_pressure_ii':
        'f8fcc246890e5b3ac9743dbd05f7f9e6ca23d9de1ba55e643f7f37bff0864aed',
    'QW2_german_advisers_ii':
        'd5ca68154beb624d0b5826b60965536ceb9c8694e49a491de83cd33e7474f6ca',
    'QW2_concessions_return':
        '415037fc11b6cfab327d1b0f149f3fcc7f2dcdf1cb1bbec601bd0a52a95a752e',
    'QW2_league_seat':
        '6e78f1f67a7db20bf44b367e0d3d00cc46249b4f8f66e1d4c079304e6caf9f2b',
    'QW2_provincial_administration':
        '168d088781492433ca192918a2ca43967da687333aab7a200dec25e17818b7d0',
    'QW2_warlord_amnesty':
        '0eee2dc095e074e9a400df25cae412ee4f137b10d8c7a0dd7697323f212fa2f5',
    'QW2_provincial_army_law':
        '05063c517a5746b64b03d7ff07741f02839b43b8fa47f3df63a149824600697e',
    'QW2_southern_integration':
        '4927eb92e01ff1ebae966a372d73cb39bd2596c32cd08d2b445d744b5ba5ce91',
    'QW2_manchurian_defence':
        '43f56e24c09ea950d788d4365c226985bf6ea8cfdea7f23be56e23cf248f7010',
    'QW2_manchurian_industry':
        '9f8373e1069d7c0839bf0f69872f8c9d0e838fe914b03e312fdc2a5b101efd9d',
    'QW2_manchurian_crisis_prep':
        '6b4bc0172ada148e07d4949ae53c2816f96a7c8fd4c5be7bd249f057ce4d99e8',
    'QW2_kmt_question':
        'b9f465dec055ab7d27e187024a0d017cb0c9ca3c7cc97391fd40695c87506ee9',
    'QW2_northern_expedition':
        '487c13460cd57dc0c78401119a5e5ce3fe9babc013a81b101ab16ababd590da7',
    'QW2_civil_service':
        '015cd71d71163e6404da55cd55fab64c8124cb3dd1eb380f0293d20c98bc6c91',
    'QW2_press_law':
        '9c89e55c190269e47b6abeb4cbcbb8c021b04150339f1a3b9d6f0aa221cd82b3',
    'QW2_local_government':
        '89bc31f3a0df8e3c3b47310b0c5fc930d98e69fc8938b111ee41ea65a5c5a179',
    'QW2_irrigation':
        'f0b2f2c6df02eac8536071afafebca46444eb2ddd6b5f723bdb7711dca99cd01',
    'QW2_road_programme':
        '2cb38f2b14d9c4749dd0d232d322e2013919ce8d33eedc113c922599ae58a247',
    'QW2_telegraph_ii':
        '2f852688d3e5c6a0897b8d26ffe845182a78fbb6502e54bb01db2b82c216b2b5',
    'QW2_tariff_policy':
        'e461d37539682a4bb00bb267f7143a5a206232a2ef6438ea4001416834ca471d',
    'QW2_army_manpower':
        '69eed07b68ef8e2aa16e57adcd9de9df8ee555c8b21b0de92b1dc167479dde96',
    'QW2_army_armour':
        'b6ab3d5ea8216e87dd8c7b8744a80144c10c0a574a7495eb599721c99351d241',
    'QW2_army_air_academy':
        'f3154a73da3d7300bad6c80a5c4eace22fdb0bef256596fa39decc58ad169022',
    'QW2_foreign_loans_ii':
        '857ef0f49f5234a2c6c0cc8536c7d64bd78b329f47247172cc97bd1a2a031dbc',
    'QW2_cultural_mission':
        '08113a81aff4ba45e25564f9e5a17c99136276e42aaba3c1104fbb3362a22594',
    'QW2_yunnan':
        'be6ba0ff6730e7e04c8b8bcff0b814c9832d2bc2512e13dba36c1c6a260f7e61',
    'QW2_tibet':
        '65e31cd43da286170899c2d841cef2509bbb3c0bec57553e66f4bbb8f82dfd2f',
    'QW2_xinjiang':
        'd9d6625a016dbe8280e6ba755b550ce4a3fe4ed5fd65eaf29542da101587b806',
    'QW2_famine_1930':
        '939b96c50611e0211796d65bef363e9dfbcf1cda6f6f0545eca547a40905b615',
    'QW2_flood_relief':
        'b5372c43d83dbe832865ba589ef2826230b9bf4a8f8300cb641ce755112727d6',
    'QW2_constitutional_press':
        '934109c4a75d9289c506557705cf5dc4eb07f65c57e0f7b0eb87c9baa500b947',
    'QW2_constitutional_judiciary':
        '7a514008d47399e86e4b3dffe8cb5c33a28c73841fbb96cf6934bd7e12f5c6bb',
    'QW2_authoritarian_prefects':
        '02bb3612ee45be9d56e2d194ebbd7499f488e0d50d889288290f801787b5463c',
    'QW2_authoritarian_court_schools':
        '28c6739228f178d5e8c3ab3b3d11d1b28000bd152ef662739148025a5532e699',
    'QW2_yuan_officers':
        '85929d8f897355f2fa82c4bc36e33b26984078ae129f7b177ad31a70f4da7ecb',
    'QW2_yuan_education':
        '420fc0246bb3b2baa4ef8d3aa112b45adfbd72cde0850710972f2f4294bed66b',
    'QW2_federal_bank':
        'b095ac1e33c979aa54c121fa23e7cee1032ea6d14d05c9e2c3daa75f704caa7b',
    'QW2_federal_police':
        'e4e60e9a1fb50ba7832667f64f7469cec073034865b12e33aa67a4eb11ac4b1e',
    'QW2_chapter_end':
        '8520f074a74eb3522256f58b845bf1af4ae4c4e953c1c0bd7d914410b88a43e9',
    'QW2_restoration_programme':
        '09a99ae140ccb834ddd50b30140154b6d3c36ecaad11105a9f4474c8091d62c2',
    'QW2_restoration_court':
        '29109f070c84ddf7d1a5741534179a646810d571b52ad898c307d1074336f629',
    'QW2_restoration_reform':
        'ea5c6869df021cdea0465a8f05aeb1d5708717891907b9e61f411b26b21a684d',
    'QW2_restoration_army':
        '16c9ffb19e0b56cdc6f756d4abd33150225b0164cdb99114a18e762725a8835f',
    'QW2_restoration_provinces':
        '97b3b59bc446dab92ab2ef51d32d305d1316d148a900b2e06fc332f87f213e3a',
    'QW2_restoration_treasury':
        'f7005b363b7e4c7861c56881575bb2489aef176119c9fbbd9147408f5f01c44a',
    'QW2_restoration_nobility':
        '0b985675091bdc73009b6f26c5b47e9e7f2d3c55a5f92fad0f5eafbfc20f14a8',
    'QW2_restoration_code':
        'b7c3cd4aecb0e0daef61b01626c276cbae64079800e4507e2995adee01b1d779',
    'QW2_restoration_guard':
        '5ba839e6af633db37a5a2d43299f7202418eea711fb039fb476efa87ddc52c76',
    'QW2_restoration_gentry':
        'e39483353c4ce33564721aa6a4bedaddc8ea07fbfa16aff37714dd7559b667a1',
    'QW2_restoration_constitution':
        'fb3537574c7d371c5482043c3a305a7e89a67d76b13ee32120f853f35b13e5b7',
    'QW2_restoration_succession':
        'd629121d188e2877dab85ed96568a4a043f91d7b559f630dfed001b643dd4eb7',
    'QW2_restoration_legation':
        '13410f28215fe2bda9715979a58965d24f5e6628954ccf162bf3a08236001e20',
    'QW2_restoration_proclaimed':
        '784235837737b5470dd8b0fb560cce77ea1e17c6e0a60f050bb3d80154ac111f',
}

FOCUS_START = re.compile(r'^\tfocus\s*=\s*\{', re.M)

# Connector geometry, mirroring the engine-facing renderer contract: a focus occupies
# 144x76 px inside a 176x116 px grid cell, and the prerequisite curve is the cubic
# from the parent's bottom centre to the child's top centre.
GRID_X = 176.0
GRID_Y = 116.0
NODE_W = 144.0
NODE_H = 76.0
SEGMENTS = 24
EPS = 1e-7
LONG_H = 8
LONG_V = 4
LONG_M = 10


def _strip_comments(text):
    out = []
    for line in text.split('\n'):
        quote = False
        cut = len(line)
        for index, char in enumerate(line):
            if char == '"':
                quote = not quote
            elif char == '#' and not quote:
                cut = index
                break
        out.append(line[:cut] + ' ' * (len(line) - cut))
    return '\n'.join(out)


def _span(text, start):
    index = text.index('{', start)
    depth = 0
    while index < len(text):
        char = text[index]
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    raise ValueError('unbalanced focus block')


def _normalise(body):
    lines = []
    for line in body.split('\n'):
        if re.match(r'^\s*[xy]\s*=\s*-?\d+\s*$', line):
            continue
        lines.append(line.rstrip())
    return '\n'.join(lines)


def parse(path):
    text = _strip_comments(open(path, encoding='utf-8-sig').read().replace('\r\n', '\n'))
    focuses = {}
    order = []
    for match in FOCUS_START.finditer(text):
        body = text[match.start():_span(text, match.start())]
        focus_id = re.search(r'\bid\s*=\s*([A-Za-z0-9_]+)', body).group(1)
        x = int(re.search(r'^\s*x\s*=\s*(-?\d+)', body, re.M).group(1))
        y = int(re.search(r'^\s*y\s*=\s*(-?\d+)', body, re.M).group(1))
        groups = re.findall(r'prerequisite\s*=\s*\{([^}]*)\}', body)
        parents = [p for group in groups for p in re.findall(r'focus\s*=\s*([A-Za-z0-9_]+)', group)]
        focuses[focus_id] = {
            'x': x,
            'y': y,
            'parents': parents,
            'digest': hashlib.sha256(_normalise(body).encode('utf-8')).hexdigest(),
        }
        order.append(focus_id)
    return focuses, order


def _curve(parent, child):
    start = (parent[0] * GRID_X + NODE_W / 2, parent[1] * GRID_Y + NODE_H)
    end = (child[0] * GRID_X + NODE_W / 2, child[1] * GRID_Y)
    middle = (start[1] + end[1]) / 2
    return start, (start[0], middle), (end[0], middle), end


def _flatten(parent, child):
    start, first, second, end = _curve(parent, child)
    points = []
    for index in range(SEGMENTS + 1):
        t = index / SEGMENTS
        u = 1 - t
        points.append((
            u ** 3 * start[0] + 3 * u * u * t * first[0] + 3 * u * t * t * second[0] + t ** 3 * end[0],
            u ** 3 * start[1] + 3 * u * u * t * first[1] + 3 * u * t * t * second[1] + t ** 3 * end[1],
        ))
    return points


def _orientation(a, b, c):
    cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    return 0 if abs(cross) <= EPS else (1 if cross > 0 else -1)


def _on_segment(point, start, end):
    if _orientation(start, end, point) != 0:
        return False
    return (min(start[0], end[0]) - EPS <= point[0] <= max(start[0], end[0]) + EPS and
            min(start[1], end[1]) - EPS <= point[1] <= max(start[1], end[1]) + EPS)


def _segments_intersect(a1, a2, b1, b2):
    o1 = _orientation(a1, a2, b1)
    o2 = _orientation(a1, a2, b2)
    o3 = _orientation(b1, b2, a1)
    o4 = _orientation(b1, b2, a2)
    if o1 * o2 < 0 and o3 * o4 < 0:
        return True
    return ((o1 == 0 and _on_segment(b1, a1, a2)) or
            (o2 == 0 and _on_segment(b2, a1, a2)) or
            (o3 == 0 and _on_segment(a1, b1, b2)) or
            (o4 == 0 and _on_segment(a2, b1, b2)))


def _polylines_intersect(first, second):
    for index in range(1, len(first)):
        for other in range(1, len(second)):
            if _segments_intersect(first[index - 1], first[index], second[other - 1], second[other]):
                return True
    return False


def connector_report(focuses):
    edges = []
    for focus_id, data in focuses.items():
        for parent in data['parents']:
            if parent in focuses:
                edges.append((parent, focus_id))
    flattened = {
        edge: _flatten((focuses[edge[0]]['x'], focuses[edge[0]]['y']),
                       (focuses[edge[1]]['x'], focuses[edge[1]]['y']))
        for edge in edges
    }
    crossings = []
    long_connectors = []
    for index, edge in enumerate(edges):
        horizontal = abs(focuses[edge[0]]['x'] - focuses[edge[1]]['x'])
        vertical = abs(focuses[edge[0]]['y'] - focuses[edge[1]]['y'])
        if horizontal > LONG_H or vertical > LONG_V or horizontal + vertical > LONG_M:
            long_connectors.append((edge, horizontal, vertical))
        for other in edges[index + 1:]:
            if set(edge) & set(other):
                continue
            first_span = sorted((focuses[edge[0]]['y'], focuses[edge[1]]['y']))
            second_span = sorted((focuses[other[0]]['y'], focuses[other[1]]['y']))
            if not max(first_span[0], second_span[0]) < min(first_span[1], second_span[1]):
                continue
            if _polylines_intersect(flattened[edge], flattened[other]):
                crossings.append((edge, other))
    return crossings, long_connectors


def problems(focuses, order, baseline=None, check_connectors=True):
    baseline = BASELINE if baseline is None else baseline
    found = []
    if len(focuses) != FOCUS_COUNT:
        found.append('declares %d focuses, expected %d' % (len(focuses), FOCUS_COUNT))
    for focus_id in sorted(set(baseline) - set(focuses)):
        found.append('missing focus %s' % focus_id)
    for focus_id in sorted(set(focuses) - set(baseline)):
        found.append('unexpected focus %s' % focus_id)
    for focus_id in sorted(set(focuses) & set(baseline)):
        if focuses[focus_id]['digest'] != baseline[focus_id]:
            found.append('%s changed outside its x/y coordinates' % focus_id)
    cells = {}
    for focus_id, data in focuses.items():
        cells.setdefault((data['x'], data['y']), []).append(focus_id)
    for cell, ids in cells.items():
        if len(ids) > 1:
            found.append('duplicate cell %s: %s' % (cell, ', '.join(sorted(ids))))
    rows = {}
    for focus_id, data in focuses.items():
        rows.setdefault(data['y'], []).append((data['x'], focus_id))
    for y, items in rows.items():
        items.sort()
        for (x1, id1), (x2, id2) in zip(items, items[1:]):
            if x2 - x1 < 2:
                found.append('row %d: %s at x=%d is %d cell from %s at x=%d'
                             % (y, id2, x2, x2 - x1, id1, x1))
    for focus_id, data in focuses.items():
        for parent in data['parents']:
            if parent not in focuses:
                found.append('%s has a prerequisite naming missing focus %s' % (focus_id, parent))
            elif focuses[parent]['y'] >= data['y']:
                found.append('%s (y=%d) is not below its prerequisite %s (y=%d)'
                             % (focus_id, data['y'], parent, focuses[parent]['y']))
        if data['x'] < 0 or data['x'] > MAX_X or data['y'] < 0 or data['y'] > MAX_Y:
            found.append('%s at (%d,%d) is outside the declared %dx%d grid'
                         % (focus_id, data['x'], data['y'], MAX_X, MAX_Y))
    if check_connectors:
        crossings, long_connectors = connector_report(focuses)
        if len(crossings) > MAX_CROSSINGS:
            for first, second in crossings[:10]:
                found.append('connector %s -> %s crosses %s -> %s' % (first + second))
        if len(long_connectors) > MAX_LONG_CONNECTORS:
            for edge, horizontal, vertical in long_connectors:
                found.append('long connector %s -> %s spans %d columns and %d rows'
                             % (edge[0], edge[1], horizontal, vertical))
    return found


def _mutant(edit):
    """Copy the tree to a temp file, apply edit(text) -> text, return the problems."""
    tmp = tempfile.mkdtemp()
    try:
        path = os.path.join(tmp, 'qing_interwar.txt')
        text = open(TREE, encoding='utf-8-sig').read()
        changed = edit(text)
        assert changed != text, 'mutation did not change the file'
        with open(path, 'w', encoding='utf-8', newline='') as handle:
            handle.write(changed)
        focuses, order = parse(path)
        return problems(focuses, order)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_identity_and_non_layout_preservation():
    focuses, order = parse(TREE)
    found = [p for p in problems(focuses, order, check_connectors=False)
             if 'cell' not in p and 'row ' not in p and 'prerequisite' not in p
             and 'outside the declared' not in p and 'does not' not in p]
    assert not found, 'non-layout content drifted:\n  ' + '\n  '.join(found)


def test_layout_invariants():
    found = problems(*parse(TREE))
    assert not found, 'layout problems:\n  ' + '\n  '.join(found)


def test_crossing_detector_sees_a_deliberate_crossing():
    """Sanity: the geometry check must report a crossing that plainly exists."""
    synthetic = {
        'a': {'x': 0, 'y': 0, 'parents': []},
        'b': {'x': 4, 'y': 1, 'parents': ['a']},
        'c': {'x': 4, 'y': 0, 'parents': []},
        'd': {'x': 0, 'y': 1, 'parents': ['c']},
    }
    crossings, _ = connector_report(synthetic)
    assert len(crossings) == 1, crossings


def test_negative_control_detects_reward_icon_and_layout_mutations():
    """Every class of edit the pass must not make has to be caught."""
    def edit(file_text, old, new):
        assert old in file_text, 'mutation anchor missing: %r' % old
        return file_text.replace(old, new, 1)

    NL = chr(10)
    TB = chr(9)
    tab2 = TB * 2
    tab3 = TB * 3

    cases = {
        # reward tuning constant renamed inside a completion_reward block
        'reward constant': lambda t: edit(
            t, 'qing_legitimacy = constant:qing_story.legitimacy_gain',
            'qing_legitimacy = constant:qing_story.legitimacy_gain_next'),
        # one extra reward line inserted into an existing block
        'extra reward line': lambda t: edit(
            t, 'add_to_variable = { qing_reform = constant:qing_story.reform_gain }',
            'add_stability = constant:qing_story.stability_gain' + NL + tab3
            + 'add_to_variable = { qing_reform = constant:qing_story.reform_gain }'),
        # different artwork, same focus
        'icon swap': lambda t: edit(
            t, 'icon = GFX_focus_generic_monarchy_1', 'icon = GFX_focus_generic_monarchy_3'),
        # a leaf renamed
        'leaf id rename': lambda t: edit(
            t, 'id = QW2_yuan_officers', 'id = QW2_yuan_officers_renamed'),
        # prerequisite repointed at a focus below the child
        'prerequisite reversed': lambda t: edit(
            t, 'prerequisite = { focus = QW2_yuan_trunk }',
            'prerequisite = { focus = QW2_restoration_proclaimed }'),
        # two focuses on one cell
        'duplicate cell': lambda t: edit(
            t, 'id = QW2_constitutional_parties' + NL + tab2 + 'icon = GFX_focus_generic_election'
            + NL + tab2 + 'x = 11',
            'id = QW2_constitutional_parties' + NL + tab2 + 'icon = GFX_focus_generic_election'
            + NL + tab2 + 'x = 9'),
        # same-row clearance below the engine minimum
        'tight row': lambda t: edit(
            t, 'id = QW2_constitutional_crisis' + NL + tab2
            + 'icon = GFX_focus_ww1_pdx_native_en1_r_parliamentary_settlement'
            + NL + tab2 + 'x = 13',
            'id = QW2_constitutional_crisis' + NL + tab2
            + 'icon = GFX_focus_ww1_pdx_native_en1_r_parliamentary_settlement'
            + NL + tab2 + 'x = 10'),
    }
    missed = []
    for name, mutation in cases.items():
        try:
            found = _mutant(mutation)
        except AssertionError:
            missed.append(name + ' (anchor missing)')
            continue
        if not found:
            missed.append(name)
    assert not missed, 'mutations the test does not detect: ' + ', '.join(missed)


def _run_all():
    failures = 0
    for name, function in sorted(globals().items()):
        if not name.startswith('test_') or not callable(function):
            continue
        try:
            function()
        except AssertionError as error:
            failures += 1
            print('FAIL %s: %s' % (name, error))
        else:
            print('PASS %s' % name)
    return failures


if __name__ == '__main__':
    raise SystemExit(1 if _run_all() else 0)
