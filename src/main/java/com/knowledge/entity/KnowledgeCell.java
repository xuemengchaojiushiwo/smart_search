package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("knowledge_cell")
public class KnowledgeCell {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long rowId;
    private Long columnId;
    private String textValue;
    private String linkUrl;
    private Long fileId;
}


