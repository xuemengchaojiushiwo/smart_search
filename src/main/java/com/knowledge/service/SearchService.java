package com.knowledge.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.knowledge.dto.SearchRequest;
import com.knowledge.entity.SearchHistory;
import com.knowledge.vo.RagResultVO;
import com.knowledge.vo.SearchResultVO;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Slf4j
@Service
public class SearchService {

    @Autowired
    private KnowledgeService knowledgeService;

    @Autowired
    private SearchHistoryService searchHistoryService;
    
    @Autowired
    private ElasticsearchService elasticsearchService;

    // 搜索知识
    public SearchResultVO searchKnowledge(SearchRequest request, Long userId) {
        // 记录搜索历史
        SearchHistory history = new SearchHistory();
        history.setUserId(userId);
        history.setQuery(request.getQuery());
        history.setSearchTime(LocalDateTime.now());
        searchHistoryService.save(history);

        // ES搜索（暂时用数据库搜索代替）
        IPage<com.knowledge.vo.KnowledgeVO> esResults = knowledgeService.searchKnowledge(
            request.getQuery(), request.getPage(), request.getSize());

        // 增加搜索次数
        esResults.getRecords().forEach(knowledge -> {
            knowledgeService.incrementSearchCount(knowledge.getId());
        });

        // RAG搜索（暂时返回空结果）
        List<RagResultVO> ragResults = new ArrayList<>();

        // 构建搜索结果
        SearchResultVO result = new SearchResultVO();
        result.setTotal(esResults.getTotal());
        result.setEsResults(esResults.getRecords());
        result.setRagResults(ragResults);

        // 更新搜索历史的结果数量
        history.setResultCount((int) esResults.getTotal());
        searchHistoryService.updateById(history);

        return result;
    }

    // 获取搜索建议
    public List<String> getSearchSuggestions(String query) {
        // 仅调用ES，失败直接抛出
        List<String> suggestions = elasticsearchService.getSearchSuggestions(query);
        log.info("获取搜索建议成功: query={}, suggestions={}", query, suggestions);
        return suggestions;
    }

    // 获取推荐问题
    public List<String> getRecommendations(Long userId, int limit) {
        // 先获取用户个人推荐
        List<String> userRecommendations = searchHistoryService.getUserRecommendations(userId, limit);

        if (userRecommendations.size() >= limit) {
            return userRecommendations.subList(0, limit);
        }

        // 如果用户推荐不够，补充全局推荐
        List<String> globalRecommendations = searchHistoryService.getGlobalRecommendations(limit - userRecommendations.size());
        userRecommendations.addAll(globalRecommendations);

        return userRecommendations;
    }

    // 获取热门搜索
    public List<String> getHotSearches(int limit) {
        return searchHistoryService.getHotSearches(limit);
    }
}
