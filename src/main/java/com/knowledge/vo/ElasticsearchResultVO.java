package com.knowledge.vo;

import lombok.Data;

import java.util.List;

/**
 * Elasticsearch搜索结果VO
 */
@Data
public class ElasticsearchResultVO {
    
    private Long id;

    private String title;

    private String content;

    private String parentId;

    private String author;

    private String tags;

    private Float score;

    private List<String> attachmentNames;

    // 高亮字段
    private String highlightTitle;

    private String highlightContent;

    private String highlightTags;

    private String highlightAttachmentNames;
}
