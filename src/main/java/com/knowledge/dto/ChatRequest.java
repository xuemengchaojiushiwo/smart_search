package com.knowledge.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import java.util.List;

@Data
public class ChatRequest {
    
    @NotBlank(message = "问题不能为空")
    private String question;
    
    private String userId;
    
    // 会话ID，用于连续对话
    private String sessionId;
    
    // 指定知识库ID列表，用于RAG对话
    private List<Long> knowledgeIds;
    
    // 是否流式响应
    private Boolean stream = false;
}