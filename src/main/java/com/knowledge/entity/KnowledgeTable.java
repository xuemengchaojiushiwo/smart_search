package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("knowledge_table")
public class KnowledgeTable {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String name;
    private Long ownerId;
    private String dept; // 简化：字符串保存部门
}


