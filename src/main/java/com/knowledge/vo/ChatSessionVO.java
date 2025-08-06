package com.knowledge.vo;

import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Data
public class ChatSessionVO {
    
    private String sessionId;

    private String sessionName;

    private String description;

    private List<Long> knowledgeIds;

    private String createdBy;

    private LocalDateTime createdTime;

    private LocalDateTime lastActiveTime;

    private Integer messageCount;

    private String status; // ACTIVE, INACTIVE, DELETED
}