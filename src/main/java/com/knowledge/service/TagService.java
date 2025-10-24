package com.knowledge.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.knowledge.entity.Knowledge;
import com.knowledge.mapper.KnowledgeMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

/**
 * 标签服务
 * 提供标签搜索、统计等功能
 */
@Slf4j
@Service
public class TagService {
    
    @Autowired
    private KnowledgeMapper knowledgeMapper;
    
    /**
     * 搜索标签
     * @param keyword 搜索关键词
     * @param limit 返回数量限制
     * @return 匹配的标签列表
     */
    public List<String> searchTags(String keyword, int limit) {
        try {
            // 查询所有知识记录，使用原生SQL查询JSONB字段
            List<Knowledge> knowledgeList = knowledgeMapper.selectList(
                new LambdaQueryWrapper<Knowledge>()
                    .eq(Knowledge::getDeleted, 0)
                    .isNotNull(Knowledge::getTags)
                    .apply("tags::text != '[]'") // 使用PostgreSQL的JSONB操作符
            );
            
            // 提取所有标签
            Set<String> allTags = new HashSet<>();
            for (Knowledge knowledge : knowledgeList) {
                if (knowledge.getTags() != null && !knowledge.getTags().isEmpty()) {
                    allTags.addAll(knowledge.getTags());
                }
            }
            
            // 根据关键词过滤标签
            String lowerKeyword = keyword.toLowerCase();
            List<String> matchedTags = allTags.stream()
                    .filter(tag -> tag.toLowerCase().contains(lowerKeyword))
                    .sorted() // 按字母顺序排序
                    .limit(limit)
                    .collect(Collectors.toList());
            
            log.info("标签搜索完成: keyword={}, 总标签数={}, 匹配数={}", keyword, allTags.size(), matchedTags.size());
            return matchedTags;
            
        } catch (Exception e) {
            log.error("标签搜索失败: keyword={}, error={}", keyword, e.getMessage(), e);
            return new ArrayList<>();
        }
    }
    
    /**
     * 获取标签建议
     * @param input 输入关键词
     * @param limit 返回数量限制
     * @return 标签建议列表
     */
    public List<String> getTagSuggestions(String input, int limit) {
        try {
            // 如果输入为空，返回热门标签
            if (input == null || input.trim().isEmpty()) {
                return getPopularTagNames(limit);
            }
            
            // 搜索匹配的标签
            List<String> matchedTags = searchTags(input, limit);
            
            // 如果匹配结果不够，补充热门标签
            if (matchedTags.size() < limit) {
                List<String> popularTags = getPopularTagNames(limit - matchedTags.size());
                for (String popularTag : popularTags) {
                    if (!matchedTags.contains(popularTag)) {
                        matchedTags.add(popularTag);
                    }
                }
            }
            
            return matchedTags.stream().limit(limit).collect(Collectors.toList());
            
        } catch (Exception e) {
            log.error("获取标签建议失败: input={}, error={}", input, e.getMessage(), e);
            return new ArrayList<>();
        }
    }
    
    /**
     * 获取热门标签
     * @param limit 返回数量限制
     * @return 热门标签列表（包含使用次数）
     */
    public List<Map<String, Object>> getPopularTags(int limit) {
        try {
            // 查询所有知识记录
            List<Knowledge> knowledgeList = knowledgeMapper.selectList(
                new LambdaQueryWrapper<Knowledge>()
                    .eq(Knowledge::getDeleted, 0)
                    .isNotNull(Knowledge::getTags)
                    .apply("tags::text != '[]'") // 使用PostgreSQL的JSONB操作符
            );
            
            // 统计标签使用次数
            Map<String, Integer> tagCountMap = new HashMap<>();
            for (Knowledge knowledge : knowledgeList) {
                if (knowledge.getTags() != null && !knowledge.getTags().isEmpty()) {
                    for (String tag : knowledge.getTags()) {
                        tagCountMap.put(tag, tagCountMap.getOrDefault(tag, 0) + 1);
                    }
                }
            }
            
            // 按使用次数排序
            List<Map<String, Object>> popularTags = tagCountMap.entrySet().stream()
                    .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
                    .limit(limit)
                    .map(entry -> {
                        Map<String, Object> tagInfo = new HashMap<>();
                        tagInfo.put("tag", entry.getKey());
                        tagInfo.put("count", entry.getValue());
                        return tagInfo;
                    })
                    .collect(Collectors.toList());
            
            log.info("热门标签获取完成: 共{}个标签", popularTags.size());
            return popularTags;
            
        } catch (Exception e) {
            log.error("获取热门标签失败: error={}", e.getMessage(), e);
            return new ArrayList<>();
        }
    }
    
    /**
     * 获取热门标签名称列表
     * @param limit 返回数量限制
     * @return 热门标签名称列表
     */
    private List<String> getPopularTagNames(int limit) {
        List<Map<String, Object>> popularTags = getPopularTags(limit);
        return popularTags.stream()
                .map(tagInfo -> (String) tagInfo.get("tag"))
                .collect(Collectors.toList());
    }
    
    /**
     * 获取所有标签
     * @return 所有不重复的标签列表
     */
    public List<String> getAllTags() {
        try {
            // 查询所有知识记录
            List<Knowledge> knowledgeList = knowledgeMapper.selectList(
                new LambdaQueryWrapper<Knowledge>()
                    .eq(Knowledge::getDeleted, 0)
                    .isNotNull(Knowledge::getTags)
                    .apply("tags::text != '[]'") // 使用PostgreSQL的JSONB操作符
            );
            
            // 提取所有标签
            Set<String> allTags = new HashSet<>();
            for (Knowledge knowledge : knowledgeList) {
                if (knowledge.getTags() != null && !knowledge.getTags().isEmpty()) {
                    allTags.addAll(knowledge.getTags());
                }
            }
            
            // 按字母顺序排序
            List<String> sortedTags = allTags.stream()
                    .sorted()
                    .collect(Collectors.toList());
            
            log.info("所有标签获取完成: 共{}个标签", sortedTags.size());
            return sortedTags;
            
        } catch (Exception e) {
            log.error("获取所有标签失败: error={}", e.getMessage(), e);
            return new ArrayList<>();
        }
    }
    
    /**
     * 获取标签统计信息
     * @return 标签统计信息
     */
    public Map<String, Object> getTagStatistics() {
        try {
            // 查询所有知识记录
            List<Knowledge> knowledgeList = knowledgeMapper.selectList(
                new LambdaQueryWrapper<Knowledge>()
                    .eq(Knowledge::getDeleted, 0)
                    .isNotNull(Knowledge::getTags)
                    .apply("tags::text != '[]'") // 使用PostgreSQL的JSONB操作符
            );
            
            // 统计信息
            int totalKnowledge = knowledgeList.size();
            int knowledgeWithTags = 0;
            int totalTagCount = 0;
            Set<String> uniqueTags = new HashSet<>();
            
            for (Knowledge knowledge : knowledgeList) {
                if (knowledge.getTags() != null && !knowledge.getTags().isEmpty()) {
                    knowledgeWithTags++;
                    totalTagCount += knowledge.getTags().size();
                    uniqueTags.addAll(knowledge.getTags());
                }
            }
            
            Map<String, Object> statistics = new HashMap<>();
            statistics.put("totalKnowledge", totalKnowledge);
            statistics.put("knowledgeWithTags", knowledgeWithTags);
            statistics.put("totalTagCount", totalTagCount);
            statistics.put("uniqueTagCount", uniqueTags.size());
            statistics.put("averageTagsPerKnowledge", knowledgeWithTags > 0 ? 
                    (double) totalTagCount / knowledgeWithTags : 0.0);
            
            log.info("标签统计完成: 总知识数={}, 有标签知识数={}, 总标签数={}, 唯一标签数={}", 
                    totalKnowledge, knowledgeWithTags, totalTagCount, uniqueTags.size());
            
            return statistics;
            
        } catch (Exception e) {
            log.error("获取标签统计失败: error={}", e.getMessage(), e);
            return new HashMap<>();
        }
    }
}
