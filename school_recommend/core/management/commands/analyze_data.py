from django.core.management.base import BaseCommand
from spark.processor import DataProcessor
import pandas as pd

class Command(BaseCommand):
    help = '分析学校数据'

    def handle(self, *args, **options):
        # 设置 pandas 显示选项
        pd.set_option('display.float_format', lambda x: '%.2f' % x)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', 20)
        pd.set_option('display.width', 1000)

        processor = DataProcessor()
        
        if not processor.load_data():
            self.stdout.write(self.style.ERROR('数据加载失败'))
            return

        # 学校统计信息
        stats = processor.analyze_school_stats()
        self.stdout.write(self.style.SUCCESS('\n=== 学校统计信息 ==='))
        for key, value in stats.items():
            formatted_key = {
                'total_schools': '学校总数',
                'avg_master': '平均硕士点数量',
                'avg_doctor': '平均博士点数量',
                'num_985': '985高校数量',
                'num_211': '211高校数量',
                'num_zihuaxian': '自划线院校数量'
            }.get(key, key)
            self.stdout.write(f'{formatted_key}: {value:,}')

        # 地理分布
        province_dist = processor.analyze_province_distribution()
        self.stdout.write(self.style.SUCCESS('\n=== 地理分布 (前10名) ==='))
        province_dist = province_dist.head(10)
        province_dist.columns = ['学校数量', '985数量', '211数量']
        self.stdout.write(str(province_dist))

        # 专业分布
        major_dist = processor.analyze_major_distribution()
        self.stdout.write(self.style.SUCCESS('\n=== 专业分布 (前10名) ==='))
        major_dist = major_dist.head(10)
        major_dist.columns = ['开设院校数', '平均招生数', '总招生数']
        self.stdout.write(str(major_dist))

        # 分数线趋势
        score_trends = processor.analyze_score_trends()
        self.stdout.write(self.style.SUCCESS('\n=== 分数线趋势 ==='))
        score_trends.columns = ['总分', '政治', '英语', '专业课一', '专业课二']
        self.stdout.write(str(score_trends))

        # 添加总结信息
        self.stdout.write(self.style.SUCCESS('\n=== 数据分析总结 ==='))
        self.stdout.write(f"1. 全国共有{stats['total_schools']}所招收研究生的高校")
        self.stdout.write(f"2. 其中包括{stats['num_985']}所985高校，{stats['num_211']}所211高校")
        self.stdout.write(f"3. {province_dist.index[0]}拥有最多的高校，共{province_dist['学校数量'].iloc[0]}所")
        
        # 计算平均分变化
        avg_scores = score_trends.groupby(level=0)['总分'].mean()
        score_change = avg_scores.pct_change() * 100
        self.stdout.write(f"4. 2023年相比2022年，平均分变化：{score_change[2023]:.1f}%")
        self.stdout.write(f"5. 2024年相比2023年，平均分变化：{score_change[2024]:.1f}%") 