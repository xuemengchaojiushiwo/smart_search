package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("knowledge_feedbacks")
public class KnowledgeFeedback {
	@TableId(type = IdType.AUTO)
	private Long id;

	private Long knowledgeId;

	private Long userId;

	private String feedbackType; // out_of_date/unclear/not_relevant

	private String content;

	private LocalDateTime createdTime;

	@TableLogic
	private Integer deleted;
}


