package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("category_change_logs")
public class CategoryChangeLog {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private Long categoryId;
    
    private String changeType;
    
    private String oldData;

    private String newData;

    private String changeReason;
    
    private String changedBy;
    
    private LocalDateTime changedTime;
    
    @TableLogic
    private Integer deleted;
}
