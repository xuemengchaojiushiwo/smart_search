package com.knowledge.controller;

import com.knowledge.dto.SearchRequest;
import com.knowledge.service.SearchService;
import com.knowledge.util.SecurityUtils;
import com.knowledge.vo.SearchResultVO;
import com.knowledge.vo.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/search")
@Tag(name = "搜索功能", description = "知识搜索相关接口")
public class SearchController {
    
    @Autowired
    private SearchService searchService;
    
    @PostMapping
    @Operation(summary = "AI智能搜索", description = "使用大模型进行智能问答搜索")
    public ApiResponse<SearchResultVO> search(
            @Parameter(description = "搜索请求", required = true) @Valid @RequestBody SearchRequest request,
            @Parameter(description = "工作空间，不传则使用用户默认工作空间", example = "WPB") @RequestParam(required = false) String workspace) {
        // 获取当前登录用户ID
        Long userId = SecurityUtils.getCurrentUserId();
        if (userId == null) {
            log.warn("无法获取当前用户ID，使用默认值1");
            userId = 1L;
        }
        
        log.info("AI智能搜索: {}, userId: {}, workspace: {}", request.getQuery(), userId, workspace);
        SearchResultVO result = searchService.searchKnowledge(request, userId, workspace);
        return ApiResponse.success(result);
    }
    
    @PostMapping("/es")
    @Operation(summary = "ES快速搜索", description = "使用Elasticsearch进行快速知识检索")
    public ApiResponse<SearchResultVO> esSearch(
            @Parameter(description = "搜索请求", required = true) @Valid @RequestBody SearchRequest request,
            @Parameter(description = "工作空间，不传则使用用户默认工作空间", example = "WPB") @RequestParam(required = false) String workspace) {
        // 获取当前登录用户ID
        Long userId = SecurityUtils.getCurrentUserId();
        if (userId == null) {
            log.warn("无法获取当前用户ID，使用默认值1");
            userId = 1L;
        }
        
        log.info("ES快速搜索: {}, userId: {}, workspace: {}", request.getQuery(), userId, workspace);
        SearchResultVO result = searchService.esSearchKnowledge(request, userId, workspace);
        return ApiResponse.success(result);
    }
    
    @GetMapping("/suggest")
    @Operation(summary = "获取搜索建议", description = "根据输入获取搜索建议")
    public ApiResponse<List<String>> getSuggestions(
            @Parameter(description = "搜索关键词", required = true, example = "知识") @RequestParam String q) {
        log.info("获取搜索建议: {}", q);
        List<String> suggestions = searchService.getSearchSuggestions(q);
        return ApiResponse.success(suggestions);
    }
    
    @GetMapping("/recommendations")
    @Operation(summary = "获取推荐问题", description = "获取推荐的问题列表")
    public ApiResponse<List<String>> getRecommendations(
            @Parameter(description = "返回数量", example = "3") @RequestParam(defaultValue = "3") int limit) {
        // 获取当前登录用户ID
        Long userId = SecurityUtils.getCurrentUserId();
        if (userId == null) {
            log.warn("无法获取当前用户ID，使用默认值1");
            userId = 1L;
        }
        
        log.info("获取推荐问题: limit={}, userId={}", limit, userId);
        List<String> recommendations = searchService.getRecommendations(userId, limit);
        return ApiResponse.success(recommendations);
    }
} 
