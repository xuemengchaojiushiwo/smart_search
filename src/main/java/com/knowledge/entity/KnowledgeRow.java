package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("knowledge_row")
public class KnowledgeRow {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long tableId;
    private Long createdBy;
}


