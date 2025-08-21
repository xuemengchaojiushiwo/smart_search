package com.knowledge.vo;

import lombok.Data;

import java.util.List;
import java.util.Map;

@Data
public class ChatMessageVO {

	private String id;
	private String sessionId;
	private String role; // user | assistant | system
	private String content;
	private List<Map<String, Object>> references; // 可选，assistant消息带溯源
	private Long timestamp;
}





