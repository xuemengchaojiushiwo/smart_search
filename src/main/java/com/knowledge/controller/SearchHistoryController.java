package com.knowledge.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.knowledge.entity.SearchHistory;
import com.knowledge.entity.User;
import com.knowledge.service.SearchHistoryService;
import com.knowledge.service.UserService;
import com.knowledge.vo.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/search/history")
@RequiredArgsConstructor
@Tag(name = "搜索历史", description = "搜索历史记录相关接口")
public class SearchHistoryController {

    private final SearchHistoryService searchHistoryService;
    
    @Autowired
    private UserService userService;

    @GetMapping
    @Operation(summary = "分页查询搜索历史", description = "获取用户的搜索历史记录")
    public ApiResponse<Page<SearchHistory>> list(
            @Parameter(description = "页码") @RequestParam(required = false) Integer page,
            @Parameter(description = "每页大小") @RequestParam(required = false) Integer size,
            @Parameter(description = "用户ID") @RequestParam(required = false) Long userId,
            @Parameter(description = "搜索关键词") @RequestParam(required = false) String keyword,
            @Parameter(description = "开始时间") @RequestParam(required = false) String startTime,
            @Parameter(description = "结束时间") @RequestParam(required = false) String endTime
    ) {
        int p = (page == null || page < 1) ? 1 : page;
        int s = (size == null || size < 1) ? 20 : size;
        
        Page<SearchHistory> pg = new Page<>(p, s);
        LambdaQueryWrapper<SearchHistory> qw = new LambdaQueryWrapper<>();
        
        // 只查询未删除的记录
        qw.eq(SearchHistory::getDeleted, 0);
        
        // 按用户ID过滤 - 如果userId是数据库ID，需要转换为staffid
        if (userId != null) {
            // 尝试将userId作为数据库ID查找用户，获取staffid
            User user = userService.getById(userId);
            if (user != null && user.getStaffId() != null) {
                try {
                    Long staffIdAsLong = Long.valueOf(user.getStaffId());
                    qw.eq(SearchHistory::getUserId, staffIdAsLong);
                } catch (NumberFormatException e) {
                    // 如果staffid不是数字，直接使用原userId
                    qw.eq(SearchHistory::getUserId, userId);
                }
            } else {
                // 如果找不到用户，直接使用原userId
                qw.eq(SearchHistory::getUserId, userId);
            }
        }
        
        // 按关键词过滤
        if (keyword != null && !keyword.isEmpty()) {
            qw.like(SearchHistory::getQuery, keyword);
        }
        
        // 按时间范围过滤
        if (startTime != null && !startTime.isEmpty()) {
            try {
                LocalDateTime start = LocalDateTime.parse(startTime);
                qw.ge(SearchHistory::getSearchTime, start);
            } catch (Exception e) {
                log.warn("开始时间格式错误: {}", startTime);
            }
        }
        
        if (endTime != null && !endTime.isEmpty()) {
            try {
                LocalDateTime end = LocalDateTime.parse(endTime);
                qw.le(SearchHistory::getSearchTime, end);
            } catch (Exception e) {
                log.warn("结束时间格式错误: {}", endTime);
            }
        }
        
        // 按搜索时间倒序排列
        qw.orderByDesc(SearchHistory::getSearchTime);
        
        Page<SearchHistory> result = searchHistoryService.page(pg, qw);
        return ApiResponse.success(result);
    }

    @GetMapping("/hot")
    @Operation(summary = "获取热门搜索", description = "获取最近的热门搜索关键词")
    public ApiResponse<List<String>> getHotSearches(
            @Parameter(description = "返回数量") @RequestParam(defaultValue = "10") int limit
    ) {
        log.info("获取热门搜索: limit={}", limit);
        List<String> hotSearches = searchHistoryService.getHotSearches(limit);
        return ApiResponse.success(hotSearches);
    }

    @GetMapping("/user/{userId}")
    @Operation(summary = "获取用户搜索历史", description = "获取指定用户的搜索历史")
    public ApiResponse<List<String>> getUserHistory(
            @Parameter(description = "用户ID") @PathVariable Long userId,
            @Parameter(description = "返回数量") @RequestParam(defaultValue = "10") int limit
    ) {
        log.info("获取用户搜索历史: userId={}, limit={}", userId, limit);
        
        // 将数据库ID转换为staffid进行查询
        Long searchUserId = userId;
        User user = userService.getById(userId);
        if (user != null && user.getStaffId() != null) {
            try {
                searchUserId = Long.valueOf(user.getStaffId());
            } catch (NumberFormatException e) {
                // 如果staffid不是数字，使用原userId
                searchUserId = userId;
            }
        }
        
        List<String> userHistory = searchHistoryService.getUserRecommendations(searchUserId, limit);
        return ApiResponse.success(userHistory);
    }

    @GetMapping("/suggestions")
    @Operation(summary = "获取搜索建议", description = "根据输入获取搜索建议")
    public ApiResponse<List<String>> getSuggestions(
            @Parameter(description = "搜索关键词") @RequestParam String q,
            @Parameter(description = "返回数量") @RequestParam(defaultValue = "5") int limit
    ) {
        log.info("获取搜索建议: q={}, limit={}", q, limit);
        List<String> suggestions = searchHistoryService.getSuggestionsFromHistory(q, limit);
        return ApiResponse.success(suggestions);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除搜索记录", description = "删除指定的搜索历史记录")
    public ApiResponse<Void> delete(
            @Parameter(description = "搜索记录ID") @PathVariable Long id
    ) {
        log.info("删除搜索记录: id={}", id);
        searchHistoryService.removeById(id);
        return ApiResponse.success(null);
    }

    @DeleteMapping("/user/{userId}")
    @Operation(summary = "清空用户搜索历史", description = "清空指定用户的所有搜索历史")
    public ApiResponse<Void> clearUserHistory(
            @Parameter(description = "用户ID") @PathVariable Long userId
    ) {
        log.info("清空用户搜索历史: userId={}", userId);
        
        // 将数据库ID转换为staffid进行查询
        Long searchUserId = userId;
        User user = userService.getById(userId);
        if (user != null && user.getStaffId() != null) {
            try {
                searchUserId = Long.valueOf(user.getStaffId());
            } catch (NumberFormatException e) {
                // 如果staffid不是数字，使用原userId
                searchUserId = userId;
            }
        }
        
        LambdaQueryWrapper<SearchHistory> qw = new LambdaQueryWrapper<>();
        qw.eq(SearchHistory::getUserId, searchUserId);
        searchHistoryService.remove(qw);
        return ApiResponse.success(null);
    }
}
