package com.knowledge.vo;

import lombok.Data;

import java.util.List;

@Data
public class SearchResultVO {
    
    private Long total;
    
    private List<KnowledgeVO> esResults;

    private List<RagResultVO> ragResults;
}
