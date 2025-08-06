package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("attachment_versions")
public class AttachmentVersion {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private Long attachmentId;
    
    private Long knowledgeId;
    
    private Long versionId;
    
    private Integer versionNumber;
    
    private String fileName;
    
    private String filePath;
    
    private Long fileSize;
    
    private String fileType;
    
    private LocalDateTime uploadTime;
    
    private Integer downloadCount;
    
    private String fileHash;
    
    private String createdBy;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdTime;
    
    @TableLogic
    private Integer deleted;
}
