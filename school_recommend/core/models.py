from django.db import models

class SchoolInfo(models.Model):
    school_id = models.IntegerField(primary_key=True, verbose_name='学校ID')
    school_name = models.CharField(max_length=255, verbose_name='学校名称')
    province_name = models.CharField(max_length=255, null=True, verbose_name='所在省份')
    province_area = models.CharField(max_length=255, null=True, verbose_name='所在地区')
    type_name = models.CharField(max_length=255, null=True, verbose_name='学校类型名称')
    type_school = models.IntegerField(null=True, verbose_name='学校类型')
    type_school_name = models.CharField(max_length=255, null=True, verbose_name='学校类型名称')
    is_985 = models.IntegerField(null=True, verbose_name='是否985院校')
    is_211 = models.IntegerField(null=True, verbose_name='是否211院校')
    is_zihuaxian = models.IntegerField(null=True, verbose_name='是否自划线院校')
    is_apply = models.IntegerField(null=True, verbose_name='是否可以直接在研招网提交报名')
    is_ads = models.IntegerField(null=True, verbose_name='是否开通百度竞价广告')
    clicks = models.IntegerField(null=True, verbose_name='学校详情点击量')
    rk_rank = models.IntegerField(null=True, verbose_name='学校软科排名')
    syl = models.IntegerField(null=True, verbose_name='考研录取率')

    class Meta:
        managed = False
        db_table = 'school_info'
        verbose_name = '学校信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.school_name

class SchoolScores(models.Model):
    school_id = models.ForeignKey(SchoolInfo, on_delete=models.CASCADE, db_column='school_id', verbose_name='学校ID')
    year = models.IntegerField(verbose_name='年份')
    degree_type = models.IntegerField(verbose_name='学位类型')
    degree_type_name = models.CharField(max_length=20, verbose_name='学位类型名称')
    special_code = models.CharField(max_length=10, verbose_name='专业代码')
    special_name = models.CharField(max_length=50, verbose_name='专业名称')
    total = models.IntegerField(default=0, verbose_name='总分')
    politics = models.IntegerField(default=0, verbose_name='政治分数')
    english = models.IntegerField(default=0, verbose_name='英语分数')
    special_one = models.IntegerField(default=0, verbose_name='专业课一分数')
    special_two = models.IntegerField(default=0, verbose_name='专业课二分数')
    note = models.CharField(max_length=255, default='', verbose_name='备注')
    diff_total = models.IntegerField(default=0, verbose_name='总分差')
    diff_politics = models.IntegerField(default=0, verbose_name='政治分差')
    diff_english = models.IntegerField(default=0, verbose_name='英语分差')
    diff_special_one = models.IntegerField(default=0, verbose_name='专业课一分差')
    diff_special_two = models.IntegerField(default=0, verbose_name='专业课二分差')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        managed = False
        db_table = 'school_scores'
        verbose_name = '学校分数线'
        verbose_name_plural = verbose_name
        unique_together = ('school_id', 'year', 'special_code')

    def __str__(self):
        return f"{self.school_id.school_name} - {self.year} - {self.special_name}"

class SchoolDetails(models.Model):
    id = models.AutoField(primary_key=True)
    school_id = models.IntegerField(null=True)
    school_name = models.CharField(max_length=255, null=True)
    province = models.CharField(max_length=100, null=True)
    top_value = models.IntegerField(null=True)
    feature = models.JSONField(null=True)
    is_211 = models.IntegerField(null=True)
    is_985 = models.IntegerField(null=True)
    is_syl = models.IntegerField(null=True)
    is_zihuaxian = models.IntegerField(null=True)
    region = models.CharField(max_length=100, null=True)
    intro = models.TextField(null=True)
    num_master = models.IntegerField(null=True)
    num_doctor = models.IntegerField(null=True)
    num_subject = models.IntegerField(null=True)
    num_lab = models.IntegerField(null=True)
    create_date = models.IntegerField(null=True)
    belongsTo = models.CharField(max_length=100, null=True)
    school_address = models.TextField(null=True)
    school_img = models.JSONField(null=True)
    phone = models.JSONField(null=True)
    site = models.JSONField(null=True)
    
    class Meta:
        managed = False
        db_table = 'school_details'

    def __str__(self):
        return f"{self.school_name}"

class PlanDetail(models.Model):
    plan_id = models.IntegerField(primary_key=True, verbose_name='招生计划ID')
    school_id = models.ForeignKey(SchoolInfo, on_delete=models.CASCADE, db_column='school_id', verbose_name='学校ID')
    year = models.IntegerField(verbose_name='招生年份')
    depart_id = models.IntegerField(null=True, verbose_name='院系所ID')
    depart_name = models.CharField(max_length=255, null=True, verbose_name='院系所名称')
    special_code = models.CharField(max_length=255, null=True, verbose_name='专业代码')
    special_name = models.CharField(max_length=255, null=True, verbose_name='专业名称')
    research_area = models.CharField(max_length=255, null=True, verbose_name='研究方向')
    exam_class = models.IntegerField(null=True, verbose_name='考试类别ID')
    exam_class_name = models.CharField(max_length=255, null=True, verbose_name='考试类别名称')
    degree_type = models.IntegerField(null=True, verbose_name='学位类型ID')
    degree_type_name = models.CharField(max_length=255, null=True, verbose_name='学位类型名称')
    recruit_type_name = models.CharField(max_length=255, null=True, verbose_name='招生类型名称')
    spe_id = models.IntegerField(null=True, verbose_name='专业ID')
    exam_subject = models.TextField(null=True, verbose_name='考试科目')
    recruit_number = models.IntegerField(null=True, verbose_name='招生人数')
    is_statistic_direction = models.IntegerField(null=True, verbose_name='是否统计到研究方向的招生人数')
    remark = models.TextField(null=True, verbose_name='备注')

    class Meta:
        managed = False
        db_table = 'plan_detail'
        verbose_name = '招生计划'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.school_id} - {self.special_name} ({self.year})"

class AnalysisResult(models.Model):
    analysis_type = models.CharField(max_length=50)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['analysis_type']),
        ]
