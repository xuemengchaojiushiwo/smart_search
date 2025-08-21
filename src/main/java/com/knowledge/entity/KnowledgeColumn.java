package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("knowledge_column")
public class KnowledgeColumn {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long tableId;
    private String name;
    private String type; // TEXT, LINK, FILE
    private Boolean required;
    private Integer sortOrder;
}


