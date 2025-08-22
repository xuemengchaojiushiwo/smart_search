package com.knowledge.vo;

import lombok.Data;

import java.util.List;

@Data
public class KnowledgeTreeVO {

    private Long id;

    private String name;

    private Long parentId;

    private String nodeType; // folder/doc

    private List<KnowledgeTreeVO> children;
}


