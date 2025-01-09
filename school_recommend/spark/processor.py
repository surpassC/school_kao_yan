import os
# 设置环境变量来指定 CPU 核心数
os.environ['LOKY_MAX_CPU_COUNT'] = '4'  # 或者设置为你的 CPU 核心数

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from scipy import stats

class DataProcessor:
    def __init__(self):
        self.conn_str = 'mysql+pymysql://root:root@localhost:3306/school_ky?charset=utf8mb4'
        
    def load_data(self):
        try:
            # 读取学校数据
            self.schools_df = pd.read_sql("""
                SELECT 
                    s.school_id,
                    s.school_name,
                    s.province_name as province,
                    s.is_985,
                    s.is_211,
                    s.is_zihuaxian,
                    d.num_master,
                    d.num_doctor,
                    d.num_lab,
                    d.num_subject
                FROM school_info s
                LEFT JOIN school_details d ON s.school_id = d.school_id
            """, self.conn_str)

            # 读取招生计划数据
            self.plans_df = pd.read_sql("""
                SELECT 
                    plan_id,
                    school_id,
                    year,
                    depart_name,
                    special_name,
                    recruit_number as plan_num
                FROM plan_detail
                WHERE recruit_number > 0
            """, self.conn_str)

            # 读取分数线数据
            self.scores_df = pd.read_sql("""
                SELECT 
                    school_id,
                    year,
                    degree_type,
                    special_name,
                    total,
                    politics,
                    english,
                    special_one,
                    special_two
                FROM school_scores
                WHERE total > 0
            """, self.conn_str)
            print("数据加载成功！")

        except Exception as e:
            print(f"数据加载错误: {str(e)}")
            raise

    def analyze_school_stats(self):
        """分析学校统计数据"""
        stats = self.schools_df.agg({
            'school_id': 'count',
            'num_master': 'mean',
            'num_doctor': 'mean',
            'is_985': lambda x: (x == 1).sum(),
            'is_211': lambda x: (x == 1).sum(),
            'is_zihuaxian': lambda x: (x == 1).sum()
        }).to_dict()
        
        return {
            'total_schools': stats['school_id'],
            'avg_master': stats['num_master'],
            'avg_doctor': stats['num_doctor'],
            'num_985': stats['is_985'],
            'num_211': stats['is_211'],
            'num_zihuaxian': stats['is_zihuaxian']
        }

    def analyze_province_distribution(self):
        """分析学校地理分布"""
        return self.schools_df.groupby('province').agg({
            'school_id': 'count',
            'is_985': lambda x: (x == 1).sum(),
            'is_211': lambda x: (x == 1).sum()
        }).rename(columns={
            'school_id': 'school_count',
            'is_985': '985_count',
            'is_211': '211_count'
        }).sort_values('school_count', ascending=False)

    def analyze_major_distribution(self):
        """分析专业分布"""
        try:
            major_distribution = self.plans_df.groupby('special_name').agg({
                'school_id': 'nunique',
                'plan_num': 'sum'
            }).reset_index()

            print("专业分布数据:", major_distribution)  # 打印数据以调试

            major_distribution['avg_students'] = major_distribution['plan_num'] / major_distribution['school_id']
            
            # 只保留前10个专业
            major_distribution = major_distribution.sort_values(by='school_id', ascending=False).head(10)

            return [
                {
                    'name': row['special_name'],
                    'school_count': int(row['school_id']),
                    'avg_students': float(row['avg_students']),
                    'total_students': int(row['plan_num'])
                }
                for _, row in major_distribution.iterrows()
            ]
            
        except Exception as e:
            print(f"专业分布分析错误: {str(e)}")
            return []

    def analyze_score_trends(self):
        """分析分数线趋势"""
        return self.scores_df.groupby(['year', 'degree_type']).agg({
            'total': 'mean',
            'politics': 'mean',
            'english': 'mean',
            'special_one': 'mean',
            'special_two': 'mean'
        }).reset_index()

    def get_top_schools(self, limit=10):
        """获取热门学校"""
        return self.plans_df.groupby('school_id').agg({
            'plan_num': 'sum'
        }).sort_values('plan_num', ascending=False).head(limit)

    def get_major_details(self, major_name):
        """获取特定专业的详细信息"""
        return self.plans_df[self.plans_df['major_name'] == major_name].merge(
            self.schools_df[['school_id', 'school_name', 'province']],
            on='school_id'
        ) 

    def analyze_region_clusters(self):
        """地域分布聚类分析"""
        try:
            # 准备数据
            features = self.schools_df.groupby('province').agg({
                'school_id': 'count',
                'is_985': lambda x: (x == 1).sum(),
                'is_211': lambda x: (x == 1).sum(),
                'num_master': 'mean',
                'num_doctor': 'mean'
            }).fillna(0)
            
            # 标准化特征
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # 聚类分析
            kmeans = KMeans(n_clusters=4, random_state=42)
            clusters = kmeans.fit_predict(features_scaled)
            
            # 准备返回数据
            result = features.copy()
            result['cluster'] = clusters
            print("地域分布聚类数据:", result)
            # 转换为列表格式
            return [
                {
                    'province': province,
                    'school_id': int(row['school_id']),
                    'is_985': int(row['is_985']),
                    'is_211': int(row['is_211']),
                    'num_master': float(row['num_master']),
                    'num_doctor': float(row['num_doctor']),
                    'cluster': int(row['cluster'])
                }
                for province, row in result.iterrows()
            ]
            
        except Exception as e:
            print(f"地域聚类分析错误: {str(e)}")
            return []

    def analyze_major_correlations(self):
        """专业相关性分析"""
        try:
            # 转换为宽格式数据
            pivot_data = self.plans_df.pivot_table(
                index='year',
                columns='major_name',
                values='plan_num',
                aggfunc='sum'
            ).fillna(0)
            
            # 计算相关系数
            corr_matrix = pivot_data.corr()
            
            # 获取相关性最强的专业对
            correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    correlations.append({
                        'major1': corr_matrix.columns[i],
                        'major2': corr_matrix.columns[j],
                        'correlation': corr_matrix.iloc[i, j]
                    })
            
            return {
                'matrix': corr_matrix.to_dict('records'),
                'top_correlations': sorted(correlations, 
                                        key=lambda x: abs(x['correlation']), 
                                        reverse=True)[:10]
            }
            
        except Exception as e:
            print(f"专业相关性分析错误: {str(e)}")
            return {'matrix': [], 'top_correlations': []}

    def predict_score_trends(self):
        """分数线趋势预测"""
        try:
            # 按年份和专业类型计算平均分
            trends = self.scores_df.groupby(['year', 'degree_type'])['total'].mean().reset_index()
            
            # 为每个学位类型建立预测模型
            predictions = []
            for degree in trends['degree_type'].unique():
                degree_data = trends[trends['degree_type'] == degree]
                
                X = degree_data['year'].values.reshape(-1, 1)
                y = degree_data['total'].values
                
                model = LinearRegression()
                model.fit(X, y)
                
                # 预测未来2年
                future_years = np.array([max(X.flatten()) + i for i in range(1, 3)])
                future_scores = model.predict(future_years.reshape(-1, 1))
                
                for year, score in zip(future_years, future_scores):
                    predictions.append({
                        'year': int(year),
                        'degree_type': degree,
                        'predicted_score': round(score, 2)
                    })
            
            return {
                'historical': trends.to_dict('records'),
                'predictions': predictions
            }
            
        except Exception as e:
            print(f"分数趋势预测错误: {str(e)}")
            return {'historical': [], 'predictions': []}

    def analyze_major_trends(self):
        """专业热度变化趋势分析"""
        try:
            # 获取最近两年的数据
            recent_years = sorted(self.plans_df['year'].unique())[-2:]
            recent_data = self.plans_df[self.plans_df['year'].isin(recent_years)]
            
            # 按年份和专业统计
            yearly_stats = recent_data.groupby(['year', 'special_name']).agg({
                'school_id': 'nunique',
                'plan_num': 'sum'
            }).reset_index()

            
            # 计算趋势
            trends = []
            for major in yearly_stats['special_name'].unique():
                major_data = yearly_stats[yearly_stats['special_name'] == major].sort_values('year')
                if len(major_data) == 2:
                    old_data = major_data.iloc[0]
                    new_data = major_data.iloc[1]
                    
                    growth_rate = ((new_data['plan_num'] / old_data['plan_num']) - 1) * 100
                    school_change = new_data['school_id'] - old_data['school_id']
                    
                    trends.append({
                        'major_name': major,
                        'growth_rate': round(growth_rate, 1),
                        'current_students': int(new_data['plan_num']),
                        'current_schools': int(new_data['school_id']),
                        'school_change': int(school_change),
                        'trend_type': 'up' if growth_rate > 10 else 'down' if growth_rate < -10 else 'stable'
                    })
            
            return sorted(trends, key=lambda x: abs(x['growth_rate']), reverse=True)[:15]
            
        except Exception as e:
            print(f"专业趋势分析错误: {str(e)}")
            return [] 