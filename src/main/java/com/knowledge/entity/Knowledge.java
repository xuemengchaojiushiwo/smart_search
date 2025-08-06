package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("knowledge")
public class Knowledge {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private String name;
    
    private String description;

    private Long categoryId;
    
    private String tags;
    
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

    @TableLogic
    private Integer deleted;
}
