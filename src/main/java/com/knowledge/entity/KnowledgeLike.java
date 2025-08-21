package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("knowledge_likes")
public class KnowledgeLike {
	@TableId(type = IdType.AUTO)
	private Long id;

	private Long knowledgeId;

	private Long userId;

	private LocalDateTime createdTime;

	@TableLogic
	private Integer deleted;
}


