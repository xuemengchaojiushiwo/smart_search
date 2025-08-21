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
import java.util.Map;

@Slf4j
@Service
public class SearchService {

    @Autowired
    private KnowledgeService knowledgeService;

    @Autowired
    private SearchHistoryService searchHistoryService;
    
    @Autowired
    private ElasticsearchService elasticsearchService;

    @Autowired
    private PythonService pythonService;

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

        // RAG检索：复用流式对话的逻辑，返回一次对话的完整回答与引用
        List<RagResultVO> ragResults = new ArrayList<>();

        String q = request.getQuery() != null ? request.getQuery().trim() : "";
        boolean looksLikeQuestion = false;
        if (!q.isEmpty()) {
            String lower = q.toLowerCase();
            looksLikeQuestion =
                q.endsWith("?") || q.endsWith("？") ||
                lower.contains("how") || lower.contains("what") || lower.contains("why") || lower.contains("which") || lower.contains("where") || lower.contains("who") || lower.contains("when") ||
                q.contains("如何") || q.contains("是什么") || q.contains("怎么") || q.contains("多少") || q.contains("为什") || q.contains("哪些") || q.contains("在哪") || q.contains("谁") || q.contains("何时") || q.contains("吗") || q.contains("么");
        }

        try {
            Map<String, Object> ragResponse = pythonService.chatWithRag(q, String.valueOf(userId));
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> references = (List<Map<String, Object>>) ragResponse.get("references");
            RagResultVO ragVo = new RagResultVO();
            String answer = (String) ragResponse.get("answer");
            ragVo.setAnswer(answer);

            if (references != null) {
                List<com.knowledge.vo.ChatResponse.KnowledgeReference> mapped = new ArrayList<>();
                for (Map<String, Object> ref : references) {
                    com.knowledge.vo.ChatResponse.KnowledgeReference kr = new com.knowledge.vo.ChatResponse.KnowledgeReference();
                    Object kid = ref.get("knowledge_id");
                    if (kid != null) {
                        try { kr.setKnowledgeId(Long.valueOf(String.valueOf(kid))); } catch (Exception ignore) {}
                    }
                    kr.setKnowledgeName((String) ref.get("knowledge_name"));
                    kr.setDescription((String) ref.get("description"));
                    Object tagsObj = ref.get("tags");
                    if (tagsObj instanceof List) {
                        @SuppressWarnings("unchecked")
                        List<String> tl = (List<String>) tagsObj;
                        kr.setTags(tl);
                    } else if (tagsObj instanceof String) {
                        String ts = (String) tagsObj;
                        kr.setTags(ts.isEmpty() ? java.util.Collections.emptyList() : java.util.Arrays.asList(ts.split(",")));
                    }
                    kr.setEffectiveTime((String) ref.get("effective_time"));
                    Object attsObj = ref.get("attachments");
                    if (attsObj instanceof List) {
                        @SuppressWarnings("unchecked")
                        List<String> al = (List<String>) attsObj;
                        kr.setAttachments(al);
                    }
                    Object rel = ref.get("relevance");
                    if (rel instanceof Number) { kr.setRelevance(((Number) rel).doubleValue()); }
                    kr.setSourceFile(ref.get("source_file") != null ? String.valueOf(ref.get("source_file")) : null);
                    if (ref.get("page_num") != null) {
                        try { kr.setPageNum(Integer.valueOf(String.valueOf(ref.get("page_num")))); } catch (Exception ignore) {}
                    }
                    if (ref.get("chunk_index") != null) {
                        try { kr.setChunkIndex(Integer.valueOf(String.valueOf(ref.get("chunk_index")))); } catch (Exception ignore) {}
                    }
                    kr.setChunkType(ref.get("chunk_type") != null ? String.valueOf(ref.get("chunk_type")) : null);
                    Object bbox = ref.get("bbox_union");
                    if (bbox instanceof List) {
                        @SuppressWarnings("unchecked")
                        List<Number> nums = (List<Number>) bbox;
                        List<Double> doubles = new ArrayList<>();
                        for (Number n : nums) { doubles.add(n.doubleValue()); }
                        kr.setBboxUnion(doubles);
                    }
                    if (ref.get("char_start") != null) {
                        try { kr.setCharStart(Integer.valueOf(String.valueOf(ref.get("char_start")))); } catch (Exception ignore) {}
                    }
                    if (ref.get("char_end") != null) {
                        try { kr.setCharEnd(Integer.valueOf(String.valueOf(ref.get("char_end")))); } catch (Exception ignore) {}
                    }
                    mapped.add(kr);
                }
                // 仅返回一个引用
                // 如果没有命中引用并且不像问句，则回退为仅推荐问题
                if (mapped.isEmpty() && !looksLikeQuestion) {
                    ragVo.setAnswer("");
                    ragVo.setReferences(java.util.Collections.emptyList());
                } else {
                    ragVo.setReferences(mapped.isEmpty() ? java.util.Collections.emptyList() : java.util.Collections.singletonList(mapped.get(0)));
                }
            } else {
                ragVo.setReferences(java.util.Collections.emptyList());
            }
            // 基于问题与答案生成两个后续建议问题（简单规则，可后续接入大模型优化）
            List<String> followUps = new ArrayList<>();
            if (q != null && !q.trim().isEmpty()) {
                followUps.add(String.format("%s 的关键依据具体在哪一页？", q));
                followUps.add(String.format("如果%s，还会有什么影响？", q));
            } else if (answer != null && !answer.trim().isEmpty()) {
                followUps.add("能否提供该结论对应的文档位置和具体段落？");
                followUps.add("该问题还有哪些相关的注意事项或限制条件？");
            } else {
                followUps.add("这条信息的来源页码和上下文是什么？");
                followUps.add("还有哪些相关内容值得进一步了解？");
            }
            ragVo.setRecommendedQuestions(followUps);
            ragResults.add(ragVo);
        } catch (Exception e) {
            log.warn("RAG检索失败，返回空rag结果: {}", e.getMessage());
            // RAG失败时回退为仅推荐问题
            RagResultVO ragVo = new RagResultVO();
            ragVo.setAnswer("");
            ragVo.setReferences(java.util.Collections.emptyList());
            List<String> followUps = new ArrayList<>();
            if (!q.isEmpty()) {
                followUps.add(String.format("如何%s？", q));
                followUps.add(String.format("%s的步骤和注意事项是什么？", q));
            } else {
                followUps.add("你想了解哪个主题的详细步骤？");
                followUps.add("是否需要我推荐一些相关问题？");
            }
            ragVo.setRecommendedQuestions(followUps);
            ragResults.add(ragVo);
        }

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
