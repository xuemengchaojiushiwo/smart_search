package com.knowledge.vo;

import lombok.Data;

@Data
public class RagResultVO {

    private String id;

    private String knowledgeId;

    private String content;

    private Float score;

    private String source;
}
