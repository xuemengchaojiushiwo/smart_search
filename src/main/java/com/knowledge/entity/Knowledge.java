package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.*;
import com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Data
@TableName(value = "knowledge", autoResultMap = true)
public class Knowledge {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private String name;
    
    private String description;
    
    private Long parentId;

    private String nodeType; // folder/doc
    
    @TableField(typeHandler = JacksonTypeHandler.class)
    private List<String> tags;

    @TableField(typeHandler = JacksonTypeHandler.class)
    private Object tableData; // 结构化表格数据：{columns:[{name,type}], rows:[...]}
    
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
