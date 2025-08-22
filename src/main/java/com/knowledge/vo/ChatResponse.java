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
        // 每个引用对应文档的下载链接（由后端拼接）。不返回整文档附件列表，只返回AI命中的块信息
        private String downloadUrl;
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
