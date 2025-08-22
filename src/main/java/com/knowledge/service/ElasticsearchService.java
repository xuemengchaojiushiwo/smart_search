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
import org.elasticsearch.search.fetch.subphase.highlight.HighlightBuilder;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
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
    public boolean indexKnowledge(Knowledge knowledge, List<Attachment> attachments) {
        try {
            Map<String, Object> document = new HashMap<>();

            // 基本信息
            document.put("id", knowledge.getId());
            document.put("title", knowledge.getName());
            document.put("content", knowledge.getDescription());
            document.put("parent_id", knowledge.getParentId());
            document.put("node_type", knowledge.getNodeType());
            document.put("tags", knowledge.getTags());
            if (knowledge.getTableData() != null) {
                document.put("table_data", knowledge.getTableData());
            }
            document.put("author", knowledge.getCreatedBy());
            document.put("status", knowledge.getStatus());
            document.put("search_count", knowledge.getSearchCount());
            document.put("download_count", knowledge.getDownloadCount());

            // 时间字段
            if (knowledge.getEffectiveStartTime() != null) {
                document.put("effective_start_time", knowledge.getEffectiveStartTime().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            }
            if (knowledge.getEffectiveEndTime() != null) {
                document.put("effective_end_time", knowledge.getEffectiveEndTime().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            }
            if (knowledge.getCreatedTime() != null) {
                document.put("created_time", knowledge.getCreatedTime().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            }
            if (knowledge.getUpdatedTime() != null) {
                document.put("updated_time", knowledge.getUpdatedTime().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            }

            // 附件信息
            if (attachments != null && !attachments.isEmpty()) {
                List<String> attachmentNames = new ArrayList<>();
                List<String> attachmentTypes = new ArrayList<>();
                long totalSize = 0;

                for (Attachment attachment : attachments) {
                    attachmentNames.add(attachment.getFileName());
                    attachmentTypes.add(attachment.getFileType());
                    totalSize += attachment.getFileSize() != null ? attachment.getFileSize() : 0;
                }

                document.put("attachment_names", attachmentNames);
                document.put("attachment_types", attachmentTypes);
                document.put("total_attachment_size", totalSize);
                document.put("attachment_count", attachments.size());
            }
            
            // 创建索引请求
            IndexRequest indexRequest = new IndexRequest(INDEX_NAME)
                    .id(knowledge.getId().toString())
                    .source(document, XContentType.JSON);
            
            elasticsearchClient.index(indexRequest, RequestOptions.DEFAULT);
            
            log.info("知识索引成功: ID={}, 标题={}", knowledge.getId(), knowledge.getName());
            return true;

        } catch (Exception e) {
            log.error("知识索引失败: ID={}", knowledge.getId(), e);
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
    public boolean updateKnowledge(Knowledge knowledge, List<Attachment> attachments) {
        try {
            Map<String, Object> document = new HashMap<>();

            // 基本信息
            document.put("title", knowledge.getName());
            document.put("content", knowledge.getDescription());
            document.put("parent_id", knowledge.getParentId());
            document.put("node_type", knowledge.getNodeType());
            document.put("tags", knowledge.getTags());
            document.put("author", knowledge.getCreatedBy());
            document.put("status", knowledge.getStatus());
            document.put("search_count", knowledge.getSearchCount());
            document.put("download_count", knowledge.getDownloadCount());
            if (knowledge.getTableData() != null) {
                document.put("table_data", knowledge.getTableData());
            }

            // 时间字段
            if (knowledge.getEffectiveStartTime() != null) {
                document.put("effective_start_time", knowledge.getEffectiveStartTime().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            }
            if (knowledge.getEffectiveEndTime() != null) {
                document.put("effective_end_time", knowledge.getEffectiveEndTime().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            }
            if (knowledge.getUpdatedTime() != null) {
                document.put("updated_time", knowledge.getUpdatedTime().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            }

            // 附件信息
            if (attachments != null && !attachments.isEmpty()) {
                List<String> attachmentNames = new ArrayList<>();
                List<String> attachmentTypes = new ArrayList<>();
                long totalSize = 0;

                for (Attachment attachment : attachments) {
                    attachmentNames.add(attachment.getFileName());
                    attachmentTypes.add(attachment.getFileType());
                    totalSize += attachment.getFileSize() != null ? attachment.getFileSize() : 0;
                }

                document.put("attachment_names", attachmentNames);
                document.put("attachment_types", attachmentTypes);
                document.put("total_attachment_size", totalSize);
                document.put("attachment_count", attachments.size());
            }

            // 创建更新请求
            UpdateRequest updateRequest = new UpdateRequest(INDEX_NAME, knowledge.getId().toString())
                    .doc(document, XContentType.JSON);

            elasticsearchClient.update(updateRequest, RequestOptions.DEFAULT);

            log.info("知识更新成功: ID={}, 标题={}", knowledge.getId(), knowledge.getName());
            return true;

        } catch (Exception e) {
            log.error("知识更新失败: ID={}", knowledge.getId(), e);
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
    public List<ElasticsearchResultVO> searchKnowledge(String query, int page, int size) {
        try {
            // 构建搜索请求
            SearchRequest searchRequest = new SearchRequest(INDEX_NAME);
            SearchSourceBuilder searchSourceBuilder = new SearchSourceBuilder();

            // 多字段匹配查询（仅针对知识元数据文档，不包含chunk内容文档）
            MultiMatchQueryBuilder multiMatchQuery = QueryBuilders.multiMatchQuery(query)
                    .field("title", 3.0f)            // 知识名称
                    .field("content", 1.5f)          // 知识描述
                    .field("tags", 2.0f)             // 标签
                    .field("attachment_names", 1.8f) // 附件文件名
                    .field("author", 1.0f)           // 作者
                    .type(MultiMatchQueryBuilder.Type.BEST_FIELDS);

            // 过滤条件：仅返回包含 source.id 的文档（知识元数据），排除chunk文档
            org.elasticsearch.index.query.BoolQueryBuilder boolQuery = QueryBuilders.boolQuery()
                    .must(multiMatchQuery)
                    .filter(QueryBuilders.existsQuery("id"));

            searchSourceBuilder.query(boolQuery);

            // 分页（加下界保护，防止 from 为负或 size 非法）
            int safePage = page > 0 ? page : 1;
            int safeSize = size > 0 ? size : 10;
            searchSourceBuilder.from((safePage - 1) * safeSize);
            searchSourceBuilder.size(safeSize);

            // 暂时移除高亮，避免因字段类型或映射差异导致查询报错

            searchRequest.source(searchSourceBuilder);

            // 执行搜索
            SearchResponse response = elasticsearchClient.search(searchRequest, RequestOptions.DEFAULT);

            // 解析结果
            List<ElasticsearchResultVO> results = new ArrayList<>();
            for (SearchHit hit : response.getHits().getHits()) {
                Map<String, Object> source = hit.getSourceAsMap();
                ElasticsearchResultVO result = new ElasticsearchResultVO();
                // 设置ID：仅在可解析为Long时设置，避免非数字ID引发异常
                Object idObj = source.get("id");
                String idStr = idObj != null ? idObj.toString() : hit.getId();
                try {
                    if (idStr != null) {
                        result.setId(Long.valueOf(idStr));
                    }
                } catch (NumberFormatException nfe) {
                    log.warn("ES文档ID非数字，跳过ID设置: {}", idStr);
                }
                result.setTitle((String) source.getOrDefault("title", ""));
                result.setContent((String) source.getOrDefault("content", ""));
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
                }

                // 设置高亮内容
                if (hit.getHighlightFields().containsKey("title")) {
                    result.setHighlightTitle(hit.getHighlightFields().get("title").fragments()[0].string());
                }
                if (hit.getHighlightFields().containsKey("content")) {
                    result.setHighlightContent(hit.getHighlightFields().get("content").fragments()[0].string());
                }
                if (hit.getHighlightFields().containsKey("tags")) {
                    result.setHighlightTags(hit.getHighlightFields().get("tags").fragments()[0].string());
                }
                if (hit.getHighlightFields().containsKey("attachment_names")) {
                    result.setHighlightAttachmentNames(hit.getHighlightFields().get("attachment_names").fragments()[0].string());
                }

                results.add(result);
            }

            log.info("搜索完成，关键词: {}, 结果数量: {}", query, results.size());
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
    public long getSearchCount(String query) {
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