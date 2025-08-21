package com.knowledge.vo;

import lombok.Data;

import java.util.List;

@Data
public class RagResultVO {

    // 一次RAG对话的完整回答
    private String answer;

    // 与流式对话一致的引用信息
    private List<ChatResponse.KnowledgeReference> references;

    // 推荐的后续提问（2条）
    private List<String> recommendedQuestions;
}
