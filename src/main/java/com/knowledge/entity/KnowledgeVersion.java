package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.*;
import com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Data
@TableName(value = "knowledge_versions", autoResultMap = true)
public class KnowledgeVersion {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private Long knowledgeId;
    
    private String name;
    
    private String description;
    
    private Long categoryId;
    
    @TableField(typeHandler = JacksonTypeHandler.class)
    private List<String> tags;
    
    private LocalDateTime effectiveStartTime;
    
    private LocalDateTime effectiveEndTime;
    
    private Integer status;
    
    private String createdBy;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdTime;
    
    private String updatedBy;
    
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedTime;
    
    private Integer searchCount;
    
    private Integer downloadCount;
    
    private Integer versionNumber;
    
    private String changeReason;
    
    @TableLogic
    private Integer deleted;
}
