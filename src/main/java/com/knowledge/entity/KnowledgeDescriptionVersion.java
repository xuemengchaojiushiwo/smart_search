package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

/**
 * 知识描述版本实体
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("knowledge_description_versions")
public class KnowledgeDescriptionVersion {
    
    /**
     * 主键ID
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;
    
    /**
     * 知识ID
     */
    @TableField("knowledge_id")
    private Long knowledgeId;
    
    /**
     * 版本号（如 'V1', 'V2', '2024-01-15' 等）
     */
    @TableField("version")
    private String version;
    
    /**
     * 版本内容（HTML格式）
     */
    @TableField("content")
    private String content;
    
    /**
     * 修改人（用户名）
     */
    @TableField("editor")
    private String editor;
    
    /**
     * 修改人ID
     */
    @TableField("editor_id")
    private Long editorId;
    
    /**
     * 创建时间
     */
    @TableField(value = "created_at", fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
    
    /**
     * 创建人
     */
    @TableField("created_by")
    private String createdBy;
    
    /**
     * 更新时间
     */
    @TableField(value = "updated_at", fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;
    
    /**
     * 更新人
     */
    @TableField("updated_by")
    private String updatedBy;
    
    /**
     * 逻辑删除：0-未删除，1-已删除
     */
    @TableLogic
    @TableField("deleted")
    private Integer deleted;
}





