package com.knowledge.dto;

import io.swagger.v3.oas.annotations.media.Schema;
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
    
    // 指定特定文件名进行RAG检索（可选）
    @Schema(description = "指定特定文件名进行RAG检索，如'安联美元基金.pdf'", example = "员工手册V2.1.pdf")
    private String sourceFile;
}