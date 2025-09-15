package com.knowledge.service;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.knowledge.entity.SearchHistory;
import com.knowledge.mapper.SearchHistoryMapper;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class SearchHistoryService extends ServiceImpl<SearchHistoryMapper, SearchHistory> {

    // 获取热门搜索
    public List<String> getHotSearches(int limit) {
        return baseMapper.selectHotSearches(limit);
    }

    // 获取用户推荐问题
    public List<String> getUserRecommendations(Long userId, int limit) {
        return baseMapper.selectUserRecommendations(userId, limit);
    }

    // 获取全局推荐问题
    public List<String> getGlobalRecommendations(int limit) {
        return baseMapper.selectGlobalRecommendations(limit);
    }
    
    // 从历史搜索中获取建议
    public List<String> getSuggestionsFromHistory(String query, int limit) {
        return baseMapper.selectSuggestionsFromHistory(query, limit);
    }
    
    // 获取用户搜索统计
    public Integer getUserSearchCount(Long userId) {
        return baseMapper.selectUserSearchCount(userId);
    }
    
    // 获取最近搜索记录
    public List<SearchHistory> getRecentSearches(Long userId, int limit) {
        return baseMapper.selectRecentSearches(userId, limit);
    }
}
