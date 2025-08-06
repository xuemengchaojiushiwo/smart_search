package com.knowledge.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import java.util.List;

@Data
public class CreateSessionRequest {
    
    @NotBlank(message = "会话名称不能为空")
    private String sessionName;
    
    private String description;
    
    // 指定知识库ID列表，用于RAG对话
    private List<Long> knowledgeIds;
}