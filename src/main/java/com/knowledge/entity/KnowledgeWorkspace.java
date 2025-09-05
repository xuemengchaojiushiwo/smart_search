package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

/**
 * 知识-工作空间 关联表
 */
@Data
@TableName("knowledge_workspace")
public class KnowledgeWorkspace {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long knowledgeId;

    private String workspace; // 例如：WPB、IWS 等
}


