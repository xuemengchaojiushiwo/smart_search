package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("attachments")
public class Attachment {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private Long knowledgeId;
    
    private String fileName;

    private String filePath;
    
    private Long fileSize;

    private String fileType;
    
    private LocalDateTime uploadTime;
    
    private Integer downloadCount;
    
    private String fileHash;  // 文件内容hash值，用于检测文件是否变化
    
    private Long versionId;   // 关联的知识版本ID
    
    private Integer versionNumber;  // 版本号

    @TableLogic
    private Integer deleted;
}
