from django.core.management.base import BaseCommand
from dashboard.models import AchievementDefinition

SEED_DATA = [
    {'slug': 'first_practice', 'name': '最初の一歩', 'description': '初めての練習を記録した', 'category': 'practice', 'icon_name': 'footsteps', 'sort_order': 1},
    {'slug': 'streak_7', 'name': '一週間の継続', 'description': '7日間連続で練習した', 'category': 'practice', 'icon_name': 'fire', 'sort_order': 2},
    {'slug': 'streak_30', 'name': '一ヶ月の継続', 'description': '30日間連続で練習した', 'category': 'practice', 'icon_name': 'flame', 'sort_order': 3},
    {'slug': 'practice_100h', 'name': '100時間マスター', 'description': '累計100時間の練習を達成', 'category': 'practice', 'icon_name': 'clock', 'sort_order': 4},
    {'slug': 'first_live', 'name': '初めてのライブ', 'description': '初めてのライブを記録した', 'category': 'live', 'icon_name': 'ticket', 'sort_order': 5},
    {'slug': 'live_10', 'name': 'ライブマスター', 'description': '10回以上のライブに参戦', 'category': 'live', 'icon_name': 'microphone', 'sort_order': 6},
    {'slug': 'first_compose', 'name': '作曲家デビュー', 'description': '最初の作曲プロジェクトを作成', 'category': 'compose', 'icon_name': 'pencil', 'sort_order': 7},
    {'slug': 'compose_done', 'name': '完成の喜び', 'description': '初めての曲を完成させた', 'category': 'compose', 'icon_name': 'star', 'sort_order': 8},
    {'slug': 'all_rounder', 'name': 'オールラウンダー', 'description': '練習・ライブ・作曲すべてを記録', 'category': 'general', 'icon_name': 'trophy', 'sort_order': 9},
]


class Command(BaseCommand):
    help = '実績定義のシードデータを投入'

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for data in SEED_DATA:
            _, was_created = AchievementDefinition.objects.update_or_create(
                slug=data['slug'],
                defaults={k: v for k, v in data.items() if k != 'slug'},
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'実績シード完了: {created}件作成, {updated}件更新'
        ))
