/*
 Navicat Premium Dump SQL

 Source Server         : docker
 Source Server Type    : MySQL
 Source Server Version : 80040 (8.0.40)
 Source Host           : localhost:3306
 Source Schema         : school_ky

 Target Server Type    : MySQL
 Target Server Version : 80040 (8.0.40)
 File Encoding         : 65001

 Date: 02/01/2025 13:52:36
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for admission_info
-- ----------------------------
DROP TABLE IF EXISTS `admission_info`;
CREATE TABLE `admission_info`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `school_id` int NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `content_id` int NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `school_id`(`school_id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 8780 CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for enroll_info
-- ----------------------------
DROP TABLE IF EXISTS `enroll_info`;
CREATE TABLE `enroll_info`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `school_id` int NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `content_id` int NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `school_id`(`school_id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 8054 CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for plan_detail
-- ----------------------------
DROP TABLE IF EXISTS `plan_detail`;
CREATE TABLE `plan_detail`  (
  `plan_id` int NOT NULL COMMENT '招生计划ID',
  `school_id` int NOT NULL COMMENT '学校ID',
  `year` int NOT NULL COMMENT '招生年份',
  `depart_id` int NULL DEFAULT NULL COMMENT '院系所ID',
  `depart_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '院系所名称',
  `special_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '专业代码',
  `special_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '专业名称',
  `research_area` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '研究方向',
  `exam_class` int NULL DEFAULT NULL COMMENT '考试类别ID',
  `exam_class_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '考试类别名称',
  `degree_type` int NULL DEFAULT NULL COMMENT '学位类型ID',
  `degree_type_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '学位类型名称',
  `recruit_type_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '招生类型名称',
  `spe_id` int NULL DEFAULT NULL COMMENT '专业ID',
  `exam_subject` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '考试科目',
  `recruit_number` int NULL DEFAULT NULL COMMENT '招生人数',
  `is_statistic_direction` int NULL DEFAULT NULL COMMENT '是否统计到研究方向的招生人数,1是0否',
  `remark` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '备注',
  PRIMARY KEY (`plan_id`) USING BTREE,
  INDEX `idx_school_id`(`school_id` ASC) USING BTREE,
  INDEX `idx_year`(`year` ASC) USING BTREE,
  INDEX `idx_spe_id`(`spe_id` ASC) USING BTREE,
  CONSTRAINT `fk_school_id` FOREIGN KEY (`school_id`) REFERENCES `school_info` (`school_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for school_details
-- ----------------------------
DROP TABLE IF EXISTS `school_details`;
CREATE TABLE `school_details`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `school_id` int NULL DEFAULT NULL,
  `school_name` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NULL DEFAULT NULL,
  `province` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NULL DEFAULT NULL,
  `top_value` int NULL DEFAULT NULL,
  `feature` json NULL,
  `is_211` tinyint NULL DEFAULT NULL,
  `is_985` tinyint NULL DEFAULT NULL,
  `is_syl` tinyint NULL DEFAULT NULL,
  `is_zihuaxian` tinyint NULL DEFAULT NULL,
  `region` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NULL DEFAULT NULL,
  `is_apply` tinyint NULL DEFAULT NULL,
  `is_tuimian` tinyint NULL DEFAULT NULL,
  `is_apply_plan` tinyint(1) NULL DEFAULT NULL,
  `is_partner` tinyint NULL DEFAULT NULL,
  `school_site` json NULL,
  `school_phone` json NULL,
  `school_email` json NULL,
  `school_video` json NULL,
  `school_volc_video` json NULL,
  `adjust_count` int NULL DEFAULT NULL,
  `intro` text CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NULL,
  `content_id` int NULL DEFAULT NULL,
  `school_rank` json NULL,
  `num_master` int NULL DEFAULT NULL,
  `num_master_2nd` int NULL DEFAULT NULL,
  `num_doctor` int NULL DEFAULT NULL,
  `num_doctor_2nd` int NULL DEFAULT NULL,
  `num_subject` int NULL DEFAULT NULL,
  `num_lab` int NULL DEFAULT NULL,
  `create_date` int NULL DEFAULT NULL,
  `belongsTo` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NULL DEFAULT NULL,
  `school_space` int NULL DEFAULT NULL,
  `school_address` text CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NULL,
  `school_img` json NULL,
  `article_list` json NULL,
  `school_up_num` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NULL DEFAULT NULL,
  `phone` json NULL,
  `site` json NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 1118 CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for school_info
-- ----------------------------
DROP TABLE IF EXISTS `school_info`;
CREATE TABLE `school_info`  (
  `school_id` int NOT NULL COMMENT '学校ID',
  `school_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '学校名称',
  `province_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '所在省份',
  `province_area` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '所在地区',
  `type_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '学校类型名称',
  `type_school` int NULL DEFAULT NULL COMMENT '学校类型',
  `type_school_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '学校类型名称',
  `is_985` int NULL DEFAULT NULL COMMENT '是否985院校,1是2否',
  `is_211` int NULL DEFAULT NULL COMMENT '是否211院校,1是2否',
  `is_zihuaxian` int NULL DEFAULT NULL COMMENT '是否自划线院校,1是2否',
  `is_apply` int NULL DEFAULT NULL COMMENT '是否可以直接在研招网提交报名,1是2否',
  `is_ads` int NULL DEFAULT NULL COMMENT '是否开通百度竞价广告,1是0否',
  `clicks` int NULL DEFAULT NULL COMMENT '学校详情点击量',
  `rk_rank` int NULL DEFAULT NULL COMMENT '学校软科排名',
  `syl` int NULL DEFAULT NULL COMMENT '考研录取率',
  PRIMARY KEY (`school_id`) USING BTREE,
  INDEX `idx_school_name`(`school_name` ASC) USING BTREE,
  INDEX `idx_province_name`(`province_name` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for school_scores
-- ----------------------------
DROP TABLE IF EXISTS `school_scores`;
CREATE TABLE `school_scores`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  `school_id` int NOT NULL COMMENT '学校ID',
  `year` int NOT NULL COMMENT '年份',
  `degree_type` tinyint NOT NULL COMMENT '学位类型:1专业型硕士,2学术型硕士',
  `degree_type_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '学位类型名称',
  `special_code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '专业代码',
  `special_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '专业名称',
  `total` int NOT NULL DEFAULT 0 COMMENT '总分',
  `politics` int NOT NULL DEFAULT 0 COMMENT '政治分数',
  `english` int NOT NULL DEFAULT 0 COMMENT '英语分数',
  `special_one` int NOT NULL DEFAULT 0 COMMENT '专业课一分数',
  `special_two` int NOT NULL DEFAULT 0 COMMENT '专业课二分数',
  `note` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '' COMMENT '备注',
  `diff_total` int NULL DEFAULT 0 COMMENT '总分差',
  `diff_politics` int NULL DEFAULT 0 COMMENT '政治分差',
  `diff_english` int NULL DEFAULT 0 COMMENT '英语分差',
  `diff_special_one` int NULL DEFAULT 0 COMMENT '专业课一分差',
  `diff_special_two` int NULL DEFAULT 0 COMMENT '专业课二分差',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `idx_school_year_special`(`school_id` ASC, `year` ASC, `special_code` ASC) USING BTREE COMMENT '学校年份专业唯一索引',
  INDEX `idx_special_code`(`special_code` ASC) USING BTREE COMMENT '专业代码索引'
) ENGINE = InnoDB AUTO_INCREMENT = 123038 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '学校考研分数线表' ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
