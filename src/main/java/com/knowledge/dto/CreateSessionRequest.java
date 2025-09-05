package com.knowledge.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import javax.validation.constraints.NotBlank;
import java.util.List;

@Data
@Schema(description = "创建会话请求")
public class CreateSessionRequest {
    
    @NotBlank(message = "用户ID不能为空")
    @Schema(description = "用户ID", example = "7", required = true)
    private String userId;
    
    @NotBlank(message = "会话名称不能为空")
    @Schema(description = "会话名称", example = "新会话", required = true)
    private String sessionName;
    
    @Schema(description = "会话ID，如果不提供则自动生成", example = "session_1234567890_abcdef")
    private String sessionId;
    
    @Schema(description = "会话描述", example = "这是一个新的对话会话")
    private String description;
    
    @Schema(description = "关联的知识ID列表", example = "[\"1\", \"2\", \"3\"]")
    private List<String> knowledgeIds;
}