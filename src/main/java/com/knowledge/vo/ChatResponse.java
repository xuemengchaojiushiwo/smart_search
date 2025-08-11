package com.knowledge.vo;

import lombok.Data;

import java.util.List;

@Data
public class ChatResponse {
    
    private String answer;
    private List<KnowledgeReference> references;
    private String sessionId;
    private Long timestamp;
    
    @Data
    public static class KnowledgeReference {
        private Long knowledgeId;
        private String knowledgeName;
        private String description;
        private List<String> tags;
        private String effectiveTime;
        private List<String> attachments;
        private Double relevance;
        // 溯源信息（来自Python RAG返回）
        private String sourceFile;
        private Integer pageNum;
        private Integer chunkIndex;
        private String chunkType;
        private List<Double> bboxUnion;
        private Integer charStart;
        private Integer charEnd;
    }
}
