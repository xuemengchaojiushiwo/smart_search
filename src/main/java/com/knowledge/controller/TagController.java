package com.knowledge.controller;

import com.knowledge.vo.ApiResponse;
import com.knowledge.service.TagService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 标签管理控制器
 * 提供标签搜索、自动完成等功能
 */
@Slf4j
@RestController
@RequestMapping("/api/tags")
@Tag(name = "标签管理", description = "标签搜索和自动完成相关接口")
public class TagController {
    
    @Autowired
    private TagService tagService;
    
    @GetMapping("/search")
    @Operation(summary = "搜索标签", description = "根据输入关键词搜索现有标签")
    public ApiResponse<List<String>> searchTags(
            @Parameter(description = "搜索关键词", required = true, example = "技术") @RequestParam String keyword,
            @Parameter(description = "返回数量限制", example = "10") @RequestParam(defaultValue = "10") int limit) {
        
        try {
            log.info("搜索标签: keyword={}, limit={}", keyword, limit);
            
            List<String> tags = tagService.searchTags(keyword, limit);
            
            log.info("标签搜索成功: keyword={}, 找到{}个标签", keyword, tags.size());
            return ApiResponse.success("标签搜索成功", tags);
            
        } catch (Exception e) {
            log.error("标签搜索失败: keyword={}, error={}", keyword, e.getMessage(), e);
            return ApiResponse.error("标签搜索失败: " + e.getMessage());
        }
    }
    
    @GetMapping("/suggest")
    @Operation(summary = "标签自动完成", description = "根据输入获取标签建议")
    public ApiResponse<List<String>> suggestTags(
            @Parameter(description = "输入关键词", required = true, example = "技") @RequestParam String input,
            @Parameter(description = "返回数量限制", example = "5") @RequestParam(defaultValue = "5") int limit) {
        
        try {
            log.info("获取标签建议: input={}, limit={}", input, limit);
            
            List<String> suggestions = tagService.getTagSuggestions(input, limit);
            
            log.info("标签建议获取成功: input={}, 找到{}个建议", input, suggestions.size());
            return ApiResponse.success("标签建议获取成功", suggestions);
            
        } catch (Exception e) {
            log.error("标签建议获取失败: input={}, error={}", input, e.getMessage(), e);
            return ApiResponse.error("标签建议获取失败: " + e.getMessage());
        }
    }
    
    @GetMapping("/popular")
    @Operation(summary = "获取热门标签", description = "获取使用频率最高的标签")
    public ApiResponse<List<Map<String, Object>>> getPopularTags(
            @Parameter(description = "返回数量限制", example = "20") @RequestParam(defaultValue = "20") int limit) {
        
        try {
            log.info("获取热门标签: limit={}", limit);
            
            List<Map<String, Object>> popularTags = tagService.getPopularTags(limit);
            
            log.info("热门标签获取成功: 找到{}个标签", popularTags.size());
            return ApiResponse.success("热门标签获取成功", popularTags);
            
        } catch (Exception e) {
            log.error("热门标签获取失败: error={}", e.getMessage(), e);
            return ApiResponse.error("热门标签获取失败: " + e.getMessage());
        }
    }
    
    @GetMapping("/all")
    @Operation(summary = "获取所有标签", description = "获取系统中所有不重复的标签")
    public ApiResponse<List<String>> getAllTags() {
        
        try {
            log.info("获取所有标签");
            
            List<String> allTags = tagService.getAllTags();
            
            log.info("所有标签获取成功: 共{}个标签", allTags.size());
            return ApiResponse.success("所有标签获取成功", allTags);
            
        } catch (Exception e) {
            log.error("所有标签获取失败: error={}", e.getMessage(), e);
            return ApiResponse.error("所有标签获取失败: " + e.getMessage());
        }
    }
    
    @GetMapping("/statistics")
    @Operation(summary = "获取标签统计", description = "获取标签使用统计信息")
    public ApiResponse<Map<String, Object>> getTagStatistics() {
        
        try {
            log.info("获取标签统计信息");
            
            Map<String, Object> statistics = tagService.getTagStatistics();
            
            log.info("标签统计获取成功");
            return ApiResponse.success("标签统计获取成功", statistics);
            
        } catch (Exception e) {
            log.error("标签统计获取失败: error={}", e.getMessage(), e);
            return ApiResponse.error("标签统计获取失败: " + e.getMessage());
        }
    }
}
