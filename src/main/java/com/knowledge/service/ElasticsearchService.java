package com.knowledge.service;

import com.knowledge.entity.Attachment;
import com.knowledge.entity.Knowledge;
import com.knowledge.vo.ElasticsearchResultVO;
import lombok.extern.slf4j.Slf4j;
import org.elasticsearch.action.delete.DeleteRequest;
import org.elasticsearch.action.index.IndexRequest;
import org.elasticsearch.action.search.SearchRequest;
import org.elasticsearch.action.search.SearchResponse;
import org.elasticsearch.action.update.UpdateRequest;
import org.elasticsearch.client.RequestOptions;
import org.elasticsearch.client.RestHighLevelClient;
import org.elasticsearch.xcontent.XContentType;
import org.elasticsearch.index.query.MultiMatchQueryBuilder;
import org.elasticsearch.index.query.QueryBuilders;
import org.elasticsearch.search.SearchHit;
import org.elasticsearch.search.builder.SearchSourceBuilder;
import org.elasticsearch.search.collapse.CollapseBuilder;
import org.elasticsearch.search.fetch.subphase.highlight.HighlightBuilder;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Elasticsearch服务
 * 提供知识检索功能
 */
@Slf4j
@Service
public class ElasticsearchService {

    @Autowired
    private RestHighLevelClient elasticsearchClient;

    private static final String INDEX_NAME = "knowledge_base_new";

    /**
     * 索引知识文档（创建或更新）
     *
     * @param knowledge 知识实体
     * @param attachments 附件列表
     * @return 是否成功
     */
    public boolean indexKnowledge(Knowledge knowledge, List<Attachment> attachments, List<String> workspaces) {
        try {
            Map<String, Object> document = new HashMap<>();

            // 基本信息 - 只设置ES mapping中存在的字段
            document.put("knowledge_id", knowledge.getId());
            document.put("knowledge_name", knowledge.getName());
            document.put("description", knowledge.getDescription());
            document.put("tags", knowledge.getTags());
            
            // 设置有效时间（使用effective_time字段）
            if (knowledge.getEffectiveStartTime() != null) {
                document.put("effective_time", knowledge.getEffectiveStartTime().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            }
            
            // 附件信息
            if (attachments != null && !attachments.isEmpty()) {
                for (Attachment attachment : attachments) {
                    document.put("attachment_name", attachment.getFileName());
                    document.put("file_type", attachment.getFileType());
                    break; // 只设置第一个附件的信息
                }
            }
            
            // 工作空间信息
            if (workspaces != null && !workspaces.isEmpty()) {
                document.put("workspaces", workspaces);
            }
            
            IndexRequest indexRequest = new IndexRequest(INDEX_NAME)
                    .id(knowledge.getId().toString())
                    .source(document, XContentType.JSON);
            
            elasticsearchClient.index(indexRequest, RequestOptions.DEFAULT);
            
            log.info("知识索引成功: ID={}, 标题={}", knowledge.getId(), knowledge.getName());
            return true;

        } catch (Exception e) {
            log.error("知识索引失败: ID={}, 错误信息: {}", knowledge.getId(), e.getMessage(), e);
            return false;
        }
    }

    /**
     * 更新知识文档
     *
     * @param knowledge 知识实体
     * @param attachments 附件列表
     * @return 是否成功
     */
    public boolean updateKnowledge(Knowledge knowledge, List<Attachment> attachments, List<String> workspaces) {
        try {
            Map<String, Object> document = new HashMap<>();

            // 基本信息 - 只设置ES mapping中存在的字段
            document.put("knowledge_id", knowledge.getId());
            document.put("knowledge_name", knowledge.getName());
            document.put("description", knowledge.getDescription());
            document.put("tags", knowledge.getTags());
            
            // 设置有效时间（使用effective_time字段）
            if (knowledge.getEffectiveStartTime() != null) {
                document.put("effective_time", knowledge.getEffectiveStartTime().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            }
            
            // 附件信息
            if (attachments != null && !attachments.isEmpty()) {
                for (Attachment attachment : attachments) {
                    document.put("attachment_name", attachment.getFileName());
                    document.put("file_type", attachment.getFileType());
                    break; // 只设置第一个附件的信息
                }
            }
            
            // 工作空间信息
            if (workspaces != null && !workspaces.isEmpty()) {
                document.put("workspaces", workspaces);
            }

            // 创建更新请求
            UpdateRequest updateRequest = new UpdateRequest(INDEX_NAME, knowledge.getId().toString())
                    .doc(document, XContentType.JSON);

            elasticsearchClient.update(updateRequest, RequestOptions.DEFAULT);

            log.info("知识更新成功: ID={}, 标题={}", knowledge.getId(), knowledge.getName());
            return true;

        } catch (Exception e) {
            log.error("知识更新失败: ID={}, 错误信息: {}", knowledge.getId(), e.getMessage(), e);
            return false;
        }
    }

    /**
     * 删除知识文档
     *
     * @param knowledgeId 知识ID
     * @return 是否成功
     */
    public boolean deleteKnowledge(Long knowledgeId) {
        try {
            DeleteRequest deleteRequest = new DeleteRequest(INDEX_NAME, knowledgeId.toString());
            elasticsearchClient.delete(deleteRequest, RequestOptions.DEFAULT);

            log.info("知识删除成功: ID={}", knowledgeId);
            return true;

        } catch (Exception e) {
            log.error("知识删除失败: ID={}", knowledgeId, e);
            return false;
        }
    }

    /**
     * 删除某个知识下某个文件对应的所有分块文档（按 knowledge_id + source_file）
     */
    public void deleteChunksByKnowledgeAndFile(Long knowledgeId, String fileName) {
        try {
            // 使用 delete-by-query REST 调用，避免高阶客户端的包兼容问题
            String endpoint = "/" + INDEX_NAME + "/_delete_by_query";
            org.elasticsearch.client.Request request = new org.elasticsearch.client.Request("POST", endpoint);
            String body = "{\n" +
                    "  \"query\": {\n" +
                    "    \"bool\": {\n" +
                    "      \"filter\": [\n" +
                    "        {\"term\": {\"knowledge_id\": " + knowledgeId + "}},\n" +
                    "        {\"term\": {\"source_file\": \"" + fileName.replace("\"", "\\\"") + "\"}}\n" +
                    "      ]\n" +
                    "    }\n" +
                    "  }\n" +
                    "}";
            request.setJsonEntity(body);
            org.elasticsearch.client.Response resp = elasticsearchClient.getLowLevelClient().performRequest(request);
            log.info("ES删除附件相关chunks完成: knowledgeId={}, fileName={}, status={}", knowledgeId, fileName, resp.getStatusLine());
        } catch (Exception e) {
            log.warn("ES删除附件相关chunks异常: knowledgeId={}, fileName={}, error={}", knowledgeId, fileName, e.getMessage());
        }
    }

    /**
     * 搜索知识
     * 支持标题、标签、内容、附件名搜索
     *
     * @param query 搜索关键词
     * @param page  页码
     * @param size  每页大小
     * @return 搜索结果
     */
    public List<ElasticsearchResultVO> searchKnowledge(String query, int page, int size, List<String> allowedWorkspaces) {
        try {
            // 构建搜索请求
            SearchRequest searchRequest = new SearchRequest(INDEX_NAME);
            SearchSourceBuilder searchSourceBuilder = new SearchSourceBuilder();

            // 多字段匹配查询（仅针对知识元数据文档，不包含chunk内容文档）
            MultiMatchQueryBuilder multiMatchQuery = QueryBuilders.multiMatchQuery(query)
                    .field("knowledge_name", 3.0f)   // 知识名称
                    .field("description", 1.5f)      // 知识描述
                    .field("tags", 2.0f)             // 标签
                    .field("attachment_name", 1.8f)  // 附件文件名
                    .type(MultiMatchQueryBuilder.Type.BEST_FIELDS);

            // 过滤条件：搜索知识内容块文档
            org.elasticsearch.index.query.BoolQueryBuilder boolQuery = QueryBuilders.boolQuery()
                    .must(multiMatchQuery)
                    .filter(QueryBuilders.existsQuery("knowledge_id"))  // 必须有knowledge_id字段
                    .filter(QueryBuilders.existsQuery("chunk_type")); // 必须有chunk_type字段（内容块）
            
            if (allowedWorkspaces != null) {
                if (allowedWorkspaces.isEmpty()) {
                    // 用户没有工作空间权限，返回空结果
                    log.info("用户没有工作空间权限，返回空结果");
                    return Collections.emptyList();
                } else {
                    boolQuery.filter(QueryBuilders.termsQuery("workspaces.keyword", allowedWorkspaces));
                    log.info("添加工作空间过滤: {}", allowedWorkspaces);
                }
            }

            // 使用collapse按knowledge_id去重
            searchSourceBuilder.query(boolQuery);
            searchSourceBuilder.collapse(new CollapseBuilder("knowledge_id"));

            // 分页（加下界保护，防止 from 为负或 size 非法）
            int safePage = page > 0 ? page : 1;
            int safeSize = size > 0 ? size : 10;
            searchSourceBuilder.from((safePage - 1) * safeSize);
            searchSourceBuilder.size(safeSize);

            // 暂时移除高亮，避免因字段类型或映射差异导致查询报错

            searchRequest.source(searchSourceBuilder);

            // 执行搜索
            log.info("执行ES搜索，查询: {}, 工作空间过滤: {}", query, allowedWorkspaces);
            SearchResponse response = elasticsearchClient.search(searchRequest, RequestOptions.DEFAULT);
            log.info("ES搜索响应，总命中数: {}", response.getHits().getTotalHits().value);

            // 解析结果（ES已经按knowledge_id去重）
            List<ElasticsearchResultVO> results = new ArrayList<>();
            for (SearchHit hit : response.getHits().getHits()) {
                Map<String, Object> source = hit.getSourceAsMap();
                
                // 获取knowledge_id
                Object idObj = source.get("knowledge_id");
                if (idObj == null) continue;
                
                Long knowledgeId;
                try {
                    knowledgeId = Long.valueOf(idObj.toString());
                } catch (NumberFormatException nfe) {
                    log.warn("ES文档knowledge_id非数字，跳过: {}", idObj);
                    continue;
                }
                
                ElasticsearchResultVO result = new ElasticsearchResultVO();
                result.setId(knowledgeId);
                result.setTitle((String) source.getOrDefault("knowledge_name", ""));
                result.setContent((String) source.getOrDefault("description", ""));
                
                // 回填父子结构
                Object parentIdObj = source.get("parent_id");
                if (parentIdObj != null) {
                    result.setParentId(parentIdObj.toString());
                }
                result.setAuthor((String) source.get("author"));
                result.setScore(hit.getScore());
                
                // 设置标签
                if (source.get("tags") != null) {
                    Object tagsObj = source.get("tags");
                    if (tagsObj instanceof String) {
                        result.setTags((String) tagsObj);
                    } else if (tagsObj instanceof List) {
                        @SuppressWarnings("unchecked")
                        List<String> tagsList = (List<String>) tagsObj;
                        result.setTags(String.join(",", tagsList));
                    }
                }

                // 设置附件信息
                if (source.get("attachment_names") != null) {
                    @SuppressWarnings("unchecked")
                    List<String> attachmentNames = (List<String>) source.get("attachment_names");
                    result.setAttachmentNames(attachmentNames);
                } else if (source.get("source_file") != null) {
                    result.setAttachmentNames(java.util.Arrays.asList((String) source.get("source_file")));
                }

                // 设置有效时间
                if (source.get("effective_time") != null) {
                    result.setEffectiveTime((String) source.get("effective_time"));
                }

                results.add(result);
            }

            log.info("搜索完成，关键词: {}, 结果数量: {}", query, results.size());
            if (results.isEmpty()) {
                log.warn("ES搜索返回空结果，查询: {}, 工作空间: {}", query, allowedWorkspaces);
            }
            return results;

        } catch (IOException e) {
            log.error("搜索知识失败", e);
            throw new RuntimeException("ES搜索失败: " + e.getMessage(), e);
        }
    }

    /**
     * 获取搜索总数
     *
     * @param query 搜索关键词
     * @return 总数
     */
    public long getSearchCount(String query, List<String> allowedWorkspaces) {
        try {
            SearchRequest searchRequest = new SearchRequest(INDEX_NAME);
            SearchSourceBuilder searchSourceBuilder = new SearchSourceBuilder();

            MultiMatchQueryBuilder multiMatchQuery = QueryBuilders.multiMatchQuery(query)
                    .field("title", 3.0f)
                    .field("content", 1.5f)
                    .field("tags", 2.0f)
                    .field("attachment_names", 1.8f)
                    .field("author", 1.0f)
                    .type(MultiMatchQueryBuilder.Type.BEST_FIELDS);

            org.elasticsearch.index.query.BoolQueryBuilder boolQuery = QueryBuilders.boolQuery()
                    .must(multiMatchQuery)
                    .filter(QueryBuilders.existsQuery("id"));
            if (allowedWorkspaces != null) {
                if (allowedWorkspaces.isEmpty()) {
                    // 用户没有工作空间权限，返回0
                    return 0;
                } else {
                    boolQuery.filter(QueryBuilders.termsQuery("workspaces.keyword", allowedWorkspaces));
                }
            }

            searchSourceBuilder.query(boolQuery);
            searchSourceBuilder.size(0); // 只获取总数，不返回文档

            searchRequest.source(searchSourceBuilder);
            SearchResponse response = elasticsearchClient.search(searchRequest, RequestOptions.DEFAULT);

            return response.getHits().getTotalHits().value;

        } catch (IOException e) {
            log.error("获取搜索总数失败", e);
            throw new RuntimeException("ES获取总数失败: " + e.getMessage(), e);
        }
    }
    
    /**
     * 获取搜索建议
     */
    public List<String> getSearchSuggestions(String query) {
        try {
            // 使用ES的completion suggester
            SearchRequest searchRequest = new SearchRequest(INDEX_NAME);
            SearchSourceBuilder searchSourceBuilder = new SearchSourceBuilder();
            
            // 使用前缀匹配来获取建议
            searchSourceBuilder.query(QueryBuilders.prefixQuery("title", query));
            searchSourceBuilder.size(5); // 限制返回数量
            
            searchRequest.source(searchSourceBuilder);
            SearchResponse response = elasticsearchClient.search(searchRequest, RequestOptions.DEFAULT);
            
            List<String> suggestions = new ArrayList<>();
            for (SearchHit hit : response.getHits().getHits()) {
                Map<String, Object> source = hit.getSourceAsMap();
                String title = (String) source.get("title");
                if (title != null && !title.equals(query)) {
                    suggestions.add(title);
                }
            }
            
            // 如果建议不够，从内容中提取
            if (suggestions.size() < 5) {
                searchSourceBuilder.query(QueryBuilders.prefixQuery("content", query));
                searchRequest.source(searchSourceBuilder);
                response = elasticsearchClient.search(searchRequest, RequestOptions.DEFAULT);
                
                for (SearchHit hit : response.getHits().getHits()) {
                    Map<String, Object> source = hit.getSourceAsMap();
                    String content = (String) source.get("content");
                    if (content != null && content.length() > 20) {
                        String suggestion = content.substring(0, Math.min(50, content.length()));
                        if (!suggestions.contains(suggestion)) {
                            suggestions.add(suggestion);
                        }
                    }
                }
            }
            
            log.info("获取搜索建议成功: query={}, suggestions={}", query, suggestions);
            return suggestions;
            
        } catch (IOException e) {
            log.error("获取搜索建议失败: query={}", query, e);
            throw new RuntimeException("ES获取搜索建议失败: " + e.getMessage(), e);
        }
    }
}