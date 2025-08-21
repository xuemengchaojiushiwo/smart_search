package com.knowledge.controller;

import com.knowledge.dto.SearchRequest;
import com.knowledge.service.SearchService;
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
    @Operation(summary = "搜索知识", description = "根据关键词搜索知识")
    public ApiResponse<SearchResultVO> search(
            @Parameter(description = "搜索请求", required = true) @Valid @RequestBody SearchRequest request) {
        // 只查ES，异常让全局异常处理
        log.info("搜索知识: {}", request.getQuery());
        SearchResultVO result = searchService.searchKnowledge(request, 1L);
        return ApiResponse.success(result);
    }
    
    @GetMapping("/suggest")
    @Operation(summary = "获取搜索建议", description = "根据输入获取搜索建议")
    public ApiResponse<List<String>> getSuggestions(
            @Parameter(description = "搜索关键�?", required = true, example = "知识") @RequestParam String q) {
        log.info("获取搜索建议: {}", q);
        List<String> suggestions = searchService.getSearchSuggestions(q);
        return ApiResponse.success(suggestions);
    }
    
    @GetMapping("/recommendations")
    @Operation(summary = "获取推荐问题", description = "获取推荐的问题列�?")
    public ApiResponse<List<String>> getRecommendations(
            @Parameter(description = "返回数量", example = "3") @RequestParam(defaultValue = "3") int limit) {
        log.info("获取推荐问题: limit={}", limit);
        // 暂时写死用户ID�?
        List<String> recommendations = searchService.getRecommendations(1L, limit);
        return ApiResponse.success(recommendations);
    }
} 
