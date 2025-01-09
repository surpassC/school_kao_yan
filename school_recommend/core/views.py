from django.db.models import Count, Q, Sum, Avg, StdDev
from django.shortcuts import render, get_object_or_404
from .models import SchoolDetails, SchoolScores, PlanDetail, SchoolInfo, AnalysisResult
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.views.generic import TemplateView
from spark.processor import DataProcessor
import pandas as pd

def index(request):
    # 获取985高校
    top_985_schools = SchoolDetails.objects.filter(
        is_985=1,
        school_id__isnull=False  # 确保有school_id
    ).order_by('-top_value')[:8]
    
    # 获取热门院校（根据学科数量排序）
    hot_schools = SchoolDetails.objects.filter(
        num_subject__isnull=False,
        school_id__isnull=False  # 确保有school_id
    ).order_by('-num_subject')[:8]
    
    # 获取高水平院校（根据top_value排序）
    top_schools = SchoolDetails.objects.filter(
        top_value__isnull=False,
        school_id__isnull=False  # 确保有school_id
    ).order_by('-top_value')[:8]
    
    # 获取各类型院校数量统计
    school_type_stats = {
        '985高校': SchoolDetails.objects.filter(is_985=1).count(),
        '211高校': SchoolDetails.objects.filter(is_211=1).count(),
        '自划线院校': SchoolDetails.objects.filter(is_zihuaxian=1).count()
    }
    
    # 获取各地区院校数量统计（按区域分组）
    region_groups = {
        'A区': ['北京', '天津', '河北', '山西', '内蒙古'],
        'B区': ['辽宁', '吉林', '黑龙江'],
        'C区': ['上海', '江苏', '浙江', '安徽'],
        'D区': ['福建', '江西', '山东', '河南'],
        'E区': ['湖北', '湖南', '广东', '广西', '海南'],
        'F区': ['重庆', '四川', '贵州', '云南', '西藏'],
        'G区': ['陕西', '甘肃', '青海', '宁夏', '新疆']
    }
    
    region_stats = {}
    for group_name, provinces in region_groups.items():
        count = SchoolDetails.objects.filter(province__in=provinces).count()
        region_stats[group_name] = {
            'provinces': '、'.join(provinces),
            'count': count
        }

    # 调试输出
    print("985高校:", [(school.school_id, school.school_name) for school in top_985_schools])
    
    context = {
        'top_985_schools': top_985_schools,
        'hot_schools': hot_schools,
        'top_schools': top_schools,
        'region_stats': region_stats,
        'school_type_stats': school_type_stats,
    }
    
    return render(request, 'core/index.html', context) 

def search(request):
    query = request.GET.get('q', '')
    if query:
        schools = SchoolDetails.objects.filter(
            Q(school_name__icontains=query) |
            Q(province__icontains=query) |
            Q(intro__icontains=query)
        ).order_by('-top_value')
    else:
        schools = SchoolDetails.objects.none()
    
    # 分页处理
    paginator = Paginator(schools, 40)  # 每页显示12所学校
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'core/search.html', context) 

def school_list(request):
    # 获取筛选参数
    region = request.GET.get('region', '')
    type = request.GET.get('type', '')
    category = request.GET.get('category', '')
    level = request.GET.get('level', '')
    
    # 基础查询
    schools = SchoolDetails.objects.all()
    
    # 应用筛选条件
    if region:
        schools = schools.filter(province=region)
    
    if type:
        if type == '985':
            schools = schools.filter(is_985=1)
        elif type == '211':
            schools = schools.filter(is_211=1)
        elif type == 'zihuaxian':
            schools = schools.filter(is_zihuaxian=1)
    
    if category:
        schools = schools.filter(feature__icontains=category)
        
    if level:
        if level == '硕士':
            schools = schools.filter(num_master__gt=0)
        elif level == '博士':
            schools = schools.filter(num_doctor__gt=0)
    
    # 分页处理
    paginator = Paginator(schools, 12)  # 每页显示12所学校
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # 获取筛选选项
    provinces = SchoolDetails.objects.values_list('province', flat=True).distinct().order_by('province')
    categories = SchoolDetails.objects.values_list('feature', flat=True).distinct().order_by('feature')
    
    context = {
        'page_obj': page_obj,
        'provinces': provinces,
        'categories': categories,
        'region': region,
        'type': type,
        'category': category,
        'level': level,
    }
    
    return render(request, 'core/school_list.html', context) 

def school_detail(request, school_id):
    # 获取当前标签页和分页参数
    active_tab = request.GET.get('tab', 'info')
    page = request.GET.get('page', 1)
    year = request.GET.get('year', 'all')
    per_page = 10
    
    # 获取学校基本信息
    school = get_object_or_404(SchoolDetails, school_id=school_id)
    
    # 获取分数线信息
    scores_query = SchoolScores.objects.filter(school_id=school_id)
    if year != 'all':
        scores_query = scores_query.filter(year=year)
    scores_query = scores_query.order_by('-year', 'special_name')
    
    # 分数线分页
    scores_paginator = Paginator(scores_query, per_page)
    try:
        latest_scores = scores_paginator.page(page if active_tab == 'scores' else 1)
    except PageNotAnInteger:
        latest_scores = scores_paginator.page(1)
    except EmptyPage:
        latest_scores = scores_paginator.page(scores_paginator.num_pages)
    
    # 获取招生计划
    plans_query = PlanDetail.objects.filter(school_id=school_id)
    if year != 'all':
        plans_query = plans_query.filter(year=year)
    plans_query = plans_query.order_by('-year', 'depart_name', 'special_name')
    
    # 招生计划分页
    plans_paginator = Paginator(plans_query, per_page)
    try:
        latest_plans = plans_paginator.page(page if active_tab == 'plans' else 1)
    except PageNotAnInteger:
        latest_plans = plans_paginator.page(1)
    except EmptyPage:
        latest_plans = plans_paginator.page(plans_paginator.num_pages)
    
    # 处理字段
    school_sites = school.site if school.site else []
    school_phones = school.phone if school.phone else []
    school_images = school.school_img if school.school_img else []  # 直接使用，不需要 json.loads
    
    context = {
        'school': school,
        'latest_scores': latest_scores,
        'latest_plans': latest_plans,
        'school_sites': school_sites,
        'school_phones': school_phones,
        'school_images': school_images,
        'available_years': [2024, 2023, 2022],
        'current_year': year,
        'active_tab': active_tab,
    }
    
    return render(request, 'core/school_detail.html', context) 

class DataAnalyticsView(TemplateView):
    template_name = 'core/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            processor = DataProcessor()
            processor.load_data()
            
            # 获取各项分析结果
            stats = processor.analyze_school_stats()
            province_dist = processor.analyze_province_distribution()
            major_dist = processor.analyze_major_distribution()
            score_trends = processor.analyze_score_trends()
            major_trends = processor.analyze_major_trends()
            
            # 转换省份分布数据
            province_data = []
            for idx, row in province_dist.head(10).iterrows():
                province_data.append({
                    'province': idx,
                    'school_count': int(row['school_count']),
                    '985_count': int(row['985_count']),
                    '211_count': int(row['211_count'])
                })

            # 准备上下文数据
            context.update({
                'school_stats': {
                    '学校总数': stats['total_schools'],
                    '985高校数量': stats['num_985'],
                    '211高校数量': stats['num_211'],
                    '自划线院校数量': stats['num_zihuaxian']
                },
                'province_distribution': province_data,
                'major_distribution': major_dist,
                'score_trends': score_trends.reset_index().to_dict('records'),
                'major_trends': json.dumps(major_trends, ensure_ascii=False),
                'has_data': True
            })
            
            # 添加地域分布聚类分析结果
            context['region_clusters'] = json.dumps(
                processor.analyze_region_clusters(),
                ensure_ascii=False
            )
            
            # 添加分数预测数据
            score_predictions = {
                'historical': [],
                'predictions': []
            }

            # 获取历史分数数据
            historical_scores = SchoolScores.objects.values(
                'year', 'degree_type_name'
            ).annotate(
                mean=Avg('total'),
                std=StdDev('total')
            ).order_by('year', 'degree_type_name')

            for score in historical_scores:
                score_predictions['historical'].append({
                    'year': score['year'],
                    'degree_type_name': score['degree_type_name'],
                    'total': {
                        'mean': float(score['mean']) if score['mean'] else 0,
                        'std': float(score['std']) if score['std'] else 0
                    }
                })

            # 添加预测数据（这里使用简单的线性预测作为示例）
            # 实际项目中应该使用更复杂的预测模型
            latest_year = max(score['year'] for score in score_predictions['historical'])
            degree_types = set(score['degree_type_name'] for score in score_predictions['historical'])

            for degree in degree_types:
                degree_scores = [s for s in score_predictions['historical'] 
                               if s['degree_type_name'] == degree]
                if degree_scores:
                    last_score = degree_scores[-1]['total']['mean']
                    # 简单预测：每年增加2分
                    for year in range(latest_year + 1, latest_year + 3):
                        score_predictions['predictions'].append({
                            'year': year,
                            'degree_type': degree,
                            'predicted_score': last_score + (year - latest_year) * 2
                        })

            context['score_predictions'] = json.dumps(score_predictions, ensure_ascii=False)
            
            # 添加招生就业关系数据
            enrollment_employment = []
            
            # 获取学校的招生和就业数据
            schools = SchoolDetails.objects.all()
            for school in schools:
                if school.num_master and school.is_syl:  # 确保有招生数据和就业率数据
                    enrollment_employment.append({
                        'school_name': school.school_name,
                        'enrollment': school.num_master,  # 招生人数
                        'employment_rate': school.is_syl,  # 就业率
                        'is_985': school.is_985 == 1,
                        'is_211': school.is_211 == 1,
                        'province': school.province
                    })

            context['enrollment_employment'] = json.dumps(enrollment_employment, ensure_ascii=False)
            
            # 添加专业热度趋势数据
            major_trends = []

            try:
                # 获取专业分布数据
                major_distribution = PlanDetail.objects.values('special_name').annotate(
                    school_count=Count('school_id', distinct=True),
                    total_students=Sum('recruit_number')
                ).filter(
                    total_students__isnull=False,
                    school_count__gt=0
                )

                print(f"Found {major_distribution.count()} majors with valid data")  # 调试输出

                # 计算平均招生规模
                avg_students = major_distribution.aggregate(
                    avg=Avg('total_students')
                )['avg'] or 0

                # 计算平均开设院校数
                avg_schools = major_distribution.aggregate(
                    avg=Avg('school_count')
                )['avg'] or 0

                # 计算趋势
                for major in major_distribution:
                    name = major['special_name']
                    total_students = major['total_students']
                    school_count = major['school_count']
                    
                    # 计算相对于平均值的偏差
                    student_ratio = (total_students - avg_students) / avg_students * 100
                    school_ratio = (school_count - avg_schools) / avg_schools * 100
                    
                    # 确定趋势类型
                    if student_ratio > 50 and school_ratio > 20:
                        trend_type = 'up'
                    elif student_ratio < -50 or school_ratio < -20:
                        trend_type = 'down'
                    else:
                        trend_type = 'stable'

                    # 计算综合热度分数
                    heat_score = (student_ratio + school_ratio) / 2

                    major_trends.append({
                        'major_name': name,
                        'current_students': total_students,
                        'current_schools': school_count,
                        'growth_rate': round(heat_score, 1),
                        'school_change': round(school_ratio, 1),
                        'trend_type': trend_type
                    })

                # 按热度分数排序
                major_trends.sort(key=lambda x: abs(x['growth_rate']), reverse=True)

                # 只取前30个专业
                major_trends = major_trends[:30]

                print(f"Generated {len(major_trends)} trend records")  # 调试输出
                if major_trends:
                    print("Sample trend:", major_trends[0])  # 调试输出

            except Exception as e:
                print(f"Error generating major trends: {str(e)}")  # 调试输出
                major_trends = []

            context['major_trends'] = json.dumps(major_trends, ensure_ascii=False)

            # 添加专业相关性热力图数据
            major_correlation = []
            try:
                # 获取招生人数最多的前20个专业
                top_majors = PlanDetail.objects.values('special_name').annotate(
                    total_students=Sum('recruit_number')
                ).order_by('-total_students')[:20]
                
                majors_list = [m['special_name'] for m in top_majors]
                
                # 预先获取所有需要的数据，减少数据库查询次数
                school_majors = {}
                major_schools = PlanDetail.objects.filter(
                    special_name__in=majors_list
                ).values('special_name', 'school_id').distinct()
                
                for record in major_schools:
                    major = record['special_name']
                    school = record['school_id']
                    if major not in school_majors:
                        school_majors[major] = set()
                    school_majors[major].add(school)

                # 计算相关性矩阵
                correlation_data = []
                for major1 in majors_list:
                    row = []
                    schools1 = school_majors.get(major1, set())
                    for major2 in majors_list:
                        schools2 = school_majors.get(major2, set())
                        
                        # 计算相关系数
                        if schools1 and schools2:
                            common_schools = len(schools1.intersection(schools2))
                            correlation = common_schools / ((len(schools1) * len(schools2)) ** 0.5)
                        else:
                            correlation = 0
                        
                        row.append(round(correlation, 2))
                    correlation_data.append(row)

                major_correlation = {
                    'majors': majors_list,
                    'data': correlation_data
                }

            except Exception as e:
                print(f"Error generating major correlation: {str(e)}")
                major_correlation = {'majors': [], 'data': []}

            context['major_correlation'] = json.dumps(major_correlation, ensure_ascii=False)

        except Exception as e:
            context['error'] = str(e)
            context['has_data'] = False
        
        return context

    def analyze_region_clusters(self):
        # 获取所有省份的学校统计数据
        provinces = SchoolDetails.objects.values('province').annotate(
            school_count=Count('school_id'),
            num_985=Count('school_id', filter=Q(is_985=1)),
            num_211=Count('school_id', filter=Q(is_211=1)),
            avg_master=Avg('num_master'),
            avg_doctor=Avg('num_doctor')
        ).filter(
            province__isnull=False,
            province__in=[
                '北京', '天津', '河北', '山西', '内蒙古', 
                '辽宁', '吉林', '黑龙江', '上海', '江苏', 
                '浙江', '安徽', '福建', '江西', '山东', 
                '河南', '湖北', '湖南', '广东', '广西', 
                '海南', '重庆', '四川', '贵州', '云南', 
                '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆'
            ]
        )

        # 计算聚类指标
        region_clusters = []
        for p in provinces:
            # 计算综合得分
            score = (
                p['school_count'] * 0.3 +
                p['num_985'] * 0.3 +
                p['num_211'] * 0.2 +
                (p['avg_master'] or 0) * 0.1 +
                (p['avg_doctor'] or 0) * 0.1
            )
            
            # 根据得分确定聚类
            if score > 20:
                cluster = 4  # 极丰富
            elif score > 15:
                cluster = 3  # 丰富
            elif score > 10:
                cluster = 2  # 较多
            elif score > 5:
                cluster = 1  # 中等
            else:
                cluster = 0  # 较少

            region_clusters.append({
                'province': p['province'],
                'cluster': cluster,
                'school_count': p['school_count'],
                'num_985': p['num_985'],
                'num_211': p['num_211'],
                'avg_master': round(p['avg_master'] or 0, 1),
                'avg_doctor': round(p['avg_doctor'] or 0, 1)
            })

        return region_clusters

def recommend(request):
    if request.method == 'POST':
        # 获取表单数据
        undergraduate_major = request.POST.get('undergraduate_major')
        target_major = request.POST.get('target_major')
        political_score = int(request.POST.get('political_score', 0))
        english_score = int(request.POST.get('english_score', 0))
        specialized_score1 = int(request.POST.get('specialized_score1', 0))
        specialized_score2 = int(request.POST.get('specialized_score2', 0))
        preferred_regions = request.POST.getlist('preferred_region')
        school_types = request.POST.getlist('school_type')
        
        # 计算总分
        total_score = political_score + english_score + specialized_score1 + (specialized_score2 if specialized_score2 else 0)
        
        # 构建推荐查询
        schools = SchoolDetails.objects.all()
        
        # 应用筛选条件
        if preferred_regions:
            schools = schools.filter(province__in=preferred_regions)
        
        if '985' in school_types:
            schools = schools.filter(is_985=1)
        if '211' in school_types:
            schools = schools.filter(is_211=1)
        
        # 根据专业和分数进行匹配
        schools = schools.order_by('-top_value')
        
        # 分页处理
        paginator = Paginator(schools, 10)  # 每页显示10所学校
        page = request.GET.get('page')
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        # 保存筛选条件到session，用于分页时保持条件
        request.session['recommend_filters'] = {
            'undergraduate_major': undergraduate_major,
            'target_major': target_major,
            'political_score': political_score,
            'english_score': english_score,
            'specialized_score1': specialized_score1,
            'specialized_score2': specialized_score2,
            'preferred_regions': preferred_regions,
            'school_types': school_types,
            'total_score': total_score,
        }
        
        context = {
            'page_obj': page_obj,
            'total_score': total_score,
            'total_count': schools.count(),
        }
        return render(request, 'core/recommend_results.html', context)
    
    # 如果是GET请求但有分页参数，说明是在查看分页结果
    elif request.GET.get('page') and 'recommend_filters' in request.session:
        filters = request.session['recommend_filters']
        schools = SchoolDetails.objects.all()
        
        # 重新应用筛选条件
        if filters.get('preferred_regions'):
            schools = schools.filter(province__in=filters['preferred_regions'])
        if '985' in filters.get('school_types', []):
            schools = schools.filter(is_985=1)
        if '211' in filters.get('school_types', []):
            schools = schools.filter(is_211=1)
            
        schools = schools.order_by('-top_value')
        
        # 分页处理
        paginator = Paginator(schools, 10)
        page = request.GET.get('page')
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
            
        context = {
            'page_obj': page_obj,
            'total_score': filters['total_score'],
            'total_count': schools.count(),
        }
        return render(request, 'core/recommend_results.html', context)
    
    # GET 请求显示表单
    context = {
        'provinces': SchoolDetails.objects.values_list('province', flat=True).distinct().order_by('province'),
        'majors': SchoolDetails.objects.values_list('feature', flat=True).distinct().order_by('feature'),
    }
    return render(request, 'core/recommend.html', context)