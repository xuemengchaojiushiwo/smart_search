package com.knowledge.controller;

import com.knowledge.service.ElasticsearchService;
import com.knowledge.vo.ApiResponse;
import com.knowledge.vo.ElasticsearchResultVO;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/elasticsearch")
@Tag(name = "Elasticsearch管理", description = "Elasticsearch相关接口")
public class ElasticsearchController {
    
    @Autowired
    private ElasticsearchService elasticsearchService;
    
    @GetMapping("/search")
    @Operation(summary = "搜索知识", description = "使用Elasticsearch搜索知识内容")
    public ApiResponse<List<ElasticsearchResultVO>> search(
            @Parameter(description = "搜索关键词", required = true) @RequestParam String query,
            @Parameter(description = "页码", example = "1") @RequestParam(defaultValue = "1") int page,
            @Parameter(description = "每页大小", example = "10") @RequestParam(defaultValue = "10") int size) {
        
        try {
            log.info("Elasticsearch搜索: query={}, page={}, size={}", query, page, size);
            List<ElasticsearchResultVO> results = elasticsearchService.searchKnowledge(query, page, size);
            return ApiResponse.success(results);
        } catch (Exception e) {
            log.error("Elasticsearch搜索失败", e);
            return ApiResponse.error("搜索失败: " + e.getMessage());
        }
    }
    
    @GetMapping("/count")
    @Operation(summary = "获取搜索总数", description = "获取搜索结果的总数")
    public ApiResponse<Long> getSearchCount(
            @Parameter(description = "搜索关键词", required = true) @RequestParam String query) {
        
        try {
            log.info("获取搜索总数: query={}", query);
            long count = elasticsearchService.getSearchCount(query);
            return ApiResponse.success(count);
        } catch (Exception e) {
            log.error("获取搜索总数失败", e);
            return ApiResponse.error("获取总数失败: " + e.getMessage());
        }
    }
}
