from django.core.management.base import BaseCommand
from spark.processor import DataProcessor

class Command(BaseCommand):
    help = '检查数据结构'

    def handle(self, *args, **options):
        # 初始化数据处理器
        processor = DataProcessor()
        processor.load_data()

        # 查看数据结构
        self.stdout.write("Province distribution columns:")
        province_dist = processor.analyze_province_distribution()
        self.stdout.write(str(province_dist.columns.tolist()))
        self.stdout.write("\nSample data:")
        self.stdout.write(str(province_dist.head()))

        self.stdout.write("\nMajor distribution columns:")
        major_dist = processor.analyze_major_distribution()
        self.stdout.write(str(major_dist.columns.tolist()))
        self.stdout.write("\nSample data:")
        self.stdout.write(str(major_dist.head()))

        self.stdout.write("\nScore trends columns:")
        score_trends = processor.analyze_score_trends()
        self.stdout.write(str(score_trends.columns.tolist()))
        self.stdout.write("\nSample data:")
        self.stdout.write(str(score_trends.head())) 