from django.shortcuts import render
from django.db.models import Q
from core.models import SchoolInfo, SchoolScores
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

def recommend_input(request):
    # 获取所有省份列表
    provinces = SchoolInfo.objects.values_list('province_name', flat=True).distinct()
    return render(request, 'recommend/input.html', {'provinces': provinces})

def recommend_results(request):
    if request.method == 'POST':
        # 获取用户输入
        politics = int(request.POST.get('politics', 0))
        english = int(request.POST.get('english', 0))
        special_one = int(request.POST.get('special_one', 0))
        special_two = int(request.POST.get('special_two', 0))
        total = politics + english + special_one + special_two
        
        degree_type = int(request.POST.get('degree_type'))
        special_code = request.POST.get('special_code')
        province = request.POST.get('province')
        
        is_985 = request.POST.get('is_985') == '1'
        is_211 = request.POST.get('is_211') == '1'
        is_zihuaxian = request.POST.get('is_zihuaxian') == '1'

        # 构建查询条件
        query = Q(special_code=special_code) & Q(degree_type=degree_type)
        
        # 获取历史分数数据
        scores = SchoolScores.objects.filter(query).select_related('school_id')
        
        # 如果有省份筛选
        if province:
            scores = scores.filter(school_id__province_name=province)
            
        # 985/211/自划线筛选
        if is_985:
            scores = scores.filter(school_id__is_985=1)
        if is_211:
            scores = scores.filter(school_id__is_211=1)
        if is_zihuaxian:
            scores = scores.filter(school_id__is_zihuaxian=1)

        # 计算相似度并推荐
        recommendations = get_recommendations(
            scores, 
            [total, politics, english, special_one, special_two]
        )

        return render(request, 'recommend/results.html', {
            'recommendations': recommendations,
            'user_scores': {
                'total': total,
                'politics': politics,
                'english': english,
                'special_one': special_one,
                'special_two': special_two,
            }
        })
    
    return render(request, 'recommend/input.html')

def get_recommendations(scores, user_scores, top_n=10):
    if not scores:
        return []
        
    # 提取历史分数特征
    features = np.array([[
        s.total, s.politics, s.english, s.special_one, s.special_two
    ] for s in scores])
    
    # 标准化
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    user_scores_scaled = scaler.transform(np.array([user_scores]))
    
    # 计算相似度
    similarities = cosine_similarity(user_scores_scaled, features_scaled)[0]
    
    # 获取推荐结果
    school_scores = list(scores)
    recommendations = []
    
    # 将相似度与学校信息组合
    for idx, similarity in enumerate(similarities):
        score = school_scores[idx]
        recommendations.append({
            'school': score.school_id,
            'score': score,
            'similarity': similarity,
            'diff_total': user_scores[0] - score.total
        })
    
    # 按相似度排序
    recommendations.sort(key=lambda x: x['similarity'], reverse=True)
    
    return recommendations[:top_n] 