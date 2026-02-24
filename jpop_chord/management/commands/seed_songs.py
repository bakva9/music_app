from django.core.management.base import BaseCommand
from jpop_chord.models import Song, ChordSection


SEED_DATA = [
    {
        'title': '紅蓮華', 'title_kana': 'ぐれんげ',
        'artist': 'LiSA', 'artist_kana': 'りさ',
        'original_key': 'Am', 'bpm': 135, 'difficulty': 3,
        'sections': [
            ('intro', 1, 4, [['Am', 'F', 'C', 'G']]),
            ('verse', 2, 8, [['Am', 'F', 'C', 'G'], ['Am', 'F', 'C', 'G']]),
            ('verse2', 3, 8, [['F', 'G', 'Am', 'Am'], ['F', 'G', 'C', 'C']]),
            ('chorus', 4, 8, [['F', 'G', 'Am', 'C'], ['F', 'G', 'Am', 'Am']]),
        ],
    },
    {
        'title': 'マリーゴールド', 'title_kana': 'まりーごーるど',
        'artist': 'あいみょん', 'artist_kana': 'あいみょん',
        'original_key': 'D', 'bpm': 107, 'difficulty': 2,
        'sections': [
            ('verse', 1, 8, [['D', 'A', 'Bm', 'G'], ['D', 'A', 'G', 'G']]),
            ('verse2', 2, 8, [['G', 'A', 'D', 'Bm'], ['G', 'A', 'D', 'D']]),
            ('chorus', 3, 8, [['G', 'A', 'D', 'Bm'], ['G', 'A', 'D', 'D']]),
        ],
    },
    {
        'title': 'Lemon', 'title_kana': 'れもん',
        'artist': '米津玄師', 'artist_kana': 'よねづけんし',
        'original_key': 'G#m', 'bpm': 87, 'difficulty': 4,
        'sections': [
            ('verse', 1, 8, [['G#m', 'E', 'B', 'F#'], ['G#m', 'E', 'B', 'F#']]),
            ('chorus', 2, 8, [['E', 'B', 'G#m', 'F#'], ['E', 'B', 'C#m', 'F#']]),
        ],
    },
    {
        'title': 'ドライフラワー', 'title_kana': 'どらいふらわー',
        'artist': '優里', 'artist_kana': 'ゆうり',
        'original_key': 'C', 'bpm': 98, 'difficulty': 2,
        'sections': [
            ('verse', 1, 8, [['C', 'G', 'Am', 'Em'], ['F', 'C', 'F', 'G']]),
            ('chorus', 2, 8, [['C', 'G', 'Am', 'Em'], ['F', 'G', 'C', 'C']]),
        ],
    },
    {
        'title': '夜に駆ける', 'title_kana': 'よるにかける',
        'artist': 'YOASOBI', 'artist_kana': 'よあそび',
        'original_key': 'Eb', 'bpm': 130, 'difficulty': 4,
        'sections': [
            ('verse', 1, 8, [['Eb', 'Cm', 'Ab', 'Bb'], ['Eb', 'Cm', 'Ab', 'Bb']]),
            ('chorus', 2, 8, [['Ab', 'Bb', 'Gm', 'Cm'], ['Ab', 'Bb', 'Eb', 'Eb']]),
        ],
    },
    {
        'title': '怪獣の花唄', 'title_kana': 'かいじゅうのはなうた',
        'artist': 'Vaundy', 'artist_kana': 'ばうんでぃ',
        'original_key': 'G', 'bpm': 120, 'difficulty': 2,
        'sections': [
            ('verse', 1, 8, [['G', 'D', 'Em', 'C'], ['G', 'D', 'C', 'C']]),
            ('chorus', 2, 8, [['C', 'D', 'G', 'Em'], ['C', 'D', 'G', 'G']]),
        ],
    },
    {
        'title': 'Subtitle', 'title_kana': 'さぶたいとる',
        'artist': 'Official髭男dism', 'artist_kana': 'おふぃしゃるひげだんでぃずむ',
        'original_key': 'Ab', 'bpm': 78, 'difficulty': 4,
        'sections': [
            ('verse', 1, 8, [['Ab', 'Eb', 'Fm', 'Db'], ['Ab', 'Eb', 'Bb', 'Bb']]),
            ('chorus', 2, 8, [['Db', 'Eb', 'Cm', 'Fm'], ['Db', 'Eb', 'Ab', 'Ab']]),
        ],
    },
    {
        'title': 'Pretender', 'title_kana': 'ぷりてんだー',
        'artist': 'Official髭男dism', 'artist_kana': 'おふぃしゃるひげだんでぃずむ',
        'original_key': 'Ab', 'bpm': 92, 'difficulty': 3,
        'sections': [
            ('verse', 1, 8, [['Ab', 'Fm', 'Db', 'Eb'], ['Ab', 'Fm', 'Db', 'Eb']]),
            ('chorus', 2, 8, [['Db', 'Eb', 'Cm', 'Fm'], ['Db', 'Eb', 'Ab', 'Ab']]),
        ],
    },
    {
        'title': '裸の心', 'title_kana': 'はだかのこころ',
        'artist': 'あいみょん', 'artist_kana': 'あいみょん',
        'original_key': 'C', 'bpm': 72, 'difficulty': 2,
        'sections': [
            ('verse', 1, 8, [['C', 'Am', 'Dm', 'G'], ['C', 'Am', 'F', 'G']]),
            ('chorus', 2, 8, [['F', 'G', 'Em', 'Am'], ['F', 'G', 'C', 'C']]),
        ],
    },
    {
        'title': '残響散歌', 'title_kana': 'ざんきょうさんか',
        'artist': 'Aimer', 'artist_kana': 'えめ',
        'original_key': 'Bm', 'bpm': 190, 'difficulty': 4,
        'sections': [
            ('verse', 1, 8, [['Bm', 'G', 'D', 'A'], ['Bm', 'G', 'D', 'A']]),
            ('chorus', 2, 8, [['G', 'A', 'Bm', 'F#m'], ['G', 'A', 'D', 'D']]),
        ],
    },
    {
        'title': '新時代', 'title_kana': 'しんじだい',
        'artist': 'Ado', 'artist_kana': 'あど',
        'original_key': 'E', 'bpm': 120, 'difficulty': 3,
        'sections': [
            ('verse', 1, 8, [['E', 'B', 'C#m', 'A'], ['E', 'B', 'A', 'A']]),
            ('chorus', 2, 8, [['A', 'B', 'G#m', 'C#m'], ['A', 'B', 'E', 'E']]),
        ],
    },
    {
        'title': '踊り子', 'title_kana': 'おどりこ',
        'artist': 'Vaundy', 'artist_kana': 'ばうんでぃ',
        'original_key': 'Dm', 'bpm': 113, 'difficulty': 3,
        'sections': [
            ('verse', 1, 8, [['Dm', 'Bb', 'F', 'C'], ['Dm', 'Bb', 'C', 'C']]),
            ('chorus', 2, 8, [['Bb', 'C', 'Am', 'Dm'], ['Bb', 'C', 'F', 'F']]),
        ],
    },
    {
        'title': 'きらり', 'title_kana': 'きらり',
        'artist': '藤井風', 'artist_kana': 'ふじいかぜ',
        'original_key': 'F', 'bpm': 110, 'difficulty': 3,
        'sections': [
            ('verse', 1, 8, [['F', 'Am', 'Bb', 'C'], ['F', 'Am', 'Bb', 'C']]),
            ('chorus', 2, 8, [['Bb', 'C', 'Am', 'Dm'], ['Bb', 'C', 'F', 'F']]),
        ],
    },
    {
        'title': 'ミックスナッツ', 'title_kana': 'みっくすなっつ',
        'artist': 'Official髭男dism', 'artist_kana': 'おふぃしゃるひげだんでぃずむ',
        'original_key': 'B', 'bpm': 155, 'difficulty': 5,
        'sections': [
            ('verse', 1, 8, [['B', 'G#m', 'E', 'F#'], ['B', 'G#m', 'E', 'F#']]),
            ('chorus', 2, 8, [['E', 'F#', 'D#m', 'G#m'], ['E', 'F#', 'B', 'B']]),
        ],
    },
    {
        'title': '群青', 'title_kana': 'ぐんじょう',
        'artist': 'YOASOBI', 'artist_kana': 'よあそび',
        'original_key': 'A', 'bpm': 136, 'difficulty': 3,
        'sections': [
            ('verse', 1, 8, [['A', 'E', 'F#m', 'D'], ['A', 'E', 'D', 'D']]),
            ('chorus', 2, 8, [['D', 'E', 'C#m', 'F#m'], ['D', 'E', 'A', 'A']]),
        ],
    },
    {
        'title': '水平線', 'title_kana': 'すいへいせん',
        'artist': 'back number', 'artist_kana': 'ばっくなんばー',
        'original_key': 'C', 'bpm': 88, 'difficulty': 2,
        'sections': [
            ('verse', 1, 8, [['C', 'G', 'Am', 'F'], ['C', 'G', 'F', 'F']]),
            ('chorus', 2, 8, [['F', 'G', 'Am', 'Em'], ['F', 'G', 'C', 'C']]),
        ],
    },
    {
        'title': 'クリスマスソング', 'title_kana': 'くりすますそんぐ',
        'artist': 'back number', 'artist_kana': 'ばっくなんばー',
        'original_key': 'G', 'bpm': 76, 'difficulty': 2,
        'sections': [
            ('verse', 1, 8, [['G', 'Em', 'C', 'D'], ['G', 'Em', 'C', 'D']]),
            ('chorus', 2, 8, [['C', 'D', 'Bm', 'Em'], ['C', 'D', 'G', 'G']]),
        ],
    },
    {
        'title': '花束', 'title_kana': 'はなたば',
        'artist': 'back number', 'artist_kana': 'ばっくなんばー',
        'original_key': 'G', 'bpm': 80, 'difficulty': 1,
        'sections': [
            ('verse', 1, 8, [['G', 'D', 'Em', 'C'], ['G', 'D', 'C', 'D']]),
            ('chorus', 2, 8, [['C', 'D', 'G', 'Em'], ['C', 'D', 'G', 'G']]),
        ],
    },
    {
        'title': 'アイドル', 'title_kana': 'あいどる',
        'artist': 'YOASOBI', 'artist_kana': 'よあそび',
        'original_key': 'Bb', 'bpm': 166, 'difficulty': 5,
        'sections': [
            ('verse', 1, 8, [['Bb', 'F', 'Gm', 'Eb'], ['Bb', 'F', 'Eb', 'Eb']]),
            ('chorus', 2, 8, [['Eb', 'F', 'Dm', 'Gm'], ['Eb', 'F', 'Bb', 'Bb']]),
        ],
    },
    {
        'title': '愛を伝えたいだとか', 'title_kana': 'あいをつたえたいだとか',
        'artist': 'あいみょん', 'artist_kana': 'あいみょん',
        'original_key': 'Em', 'bpm': 120, 'difficulty': 2,
        'sections': [
            ('verse', 1, 8, [['Em', 'C', 'G', 'D'], ['Em', 'C', 'G', 'D']]),
            ('chorus', 2, 8, [['C', 'D', 'Bm', 'Em'], ['C', 'D', 'G', 'G']]),
        ],
    },
    {
        'title': 'KICK BACK', 'title_kana': 'きっくばっく',
        'artist': '米津玄師', 'artist_kana': 'よねづけんし',
        'original_key': 'A', 'bpm': 150, 'difficulty': 4,
        'sections': [
            ('verse', 1, 8, [['A', 'F#m', 'D', 'E'], ['A', 'F#m', 'D', 'E']]),
            ('chorus', 2, 8, [['D', 'E', 'C#m', 'F#m'], ['D', 'E', 'A', 'A']]),
        ],
    },
    {
        'title': 'チェリー', 'title_kana': 'ちぇりー',
        'artist': 'スピッツ', 'artist_kana': 'すぴっつ',
        'original_key': 'C', 'bpm': 100, 'difficulty': 1,
        'sections': [
            ('verse', 1, 8, [['C', 'G', 'Am', 'Em'], ['F', 'C', 'Dm', 'G']]),
            ('chorus', 2, 8, [['F', 'G', 'C', 'Am'], ['F', 'G', 'C', 'C']]),
        ],
    },
    {
        'title': '空も飛べるはず', 'title_kana': 'そらもとべるはず',
        'artist': 'スピッツ', 'artist_kana': 'すぴっつ',
        'original_key': 'C', 'bpm': 104, 'difficulty': 1,
        'sections': [
            ('verse', 1, 8, [['C', 'Em', 'F', 'G'], ['C', 'Em', 'F', 'G']]),
            ('chorus', 2, 8, [['F', 'G', 'Em', 'Am'], ['F', 'G', 'C', 'C']]),
        ],
    },
    {
        'title': '丸の内サディスティック', 'title_kana': 'まるのうちさでぃすてぃっく',
        'artist': '椎名林檎', 'artist_kana': 'しいなりんご',
        'original_key': 'Eb', 'bpm': 100, 'difficulty': 5,
        'sections': [
            ('verse', 1, 8, [['Ebmaj7', 'Gm7', 'Abmaj7', 'Bb7'], ['Ebmaj7', 'Gm7', 'Abmaj7', 'Bb7']]),
            ('chorus', 2, 8, [['Abmaj7', 'Bb7', 'Gm7', 'Cm7'], ['Abmaj7', 'Bb7', 'Ebmaj7', 'Ebmaj7']]),
        ],
    },
    {
        'title': '可愛くてごめん', 'title_kana': 'かわいくてごめん',
        'artist': 'HoneyWorks', 'artist_kana': 'はにーわーくす',
        'original_key': 'D', 'bpm': 180, 'difficulty': 3,
        'sections': [
            ('verse', 1, 8, [['D', 'A', 'Bm', 'G'], ['D', 'A', 'G', 'A']]),
            ('chorus', 2, 8, [['G', 'A', 'F#m', 'Bm'], ['G', 'A', 'D', 'D']]),
        ],
    },
]


class Command(BaseCommand):
    help = 'シードデータ（J-POP曲）をデータベースに投入します'

    def handle(self, *args, **options):
        created_count = 0
        for data in SEED_DATA:
            sections = data.pop('sections')
            song, created = Song.objects.get_or_create(
                title=data['title'],
                artist=data['artist'],
                defaults=data,
            )
            if created:
                created_count += 1
                for section_type, order, bar_count, chords in sections:
                    ChordSection.objects.create(
                        song=song,
                        section_type=section_type,
                        order=order,
                        bar_count=bar_count,
                        chords=chords,
                    )
            data['sections'] = sections  # restore for safety

        self.stdout.write(self.style.SUCCESS(
            f'{created_count}曲を追加しました（合計: {Song.objects.count()}曲）'
        ))
