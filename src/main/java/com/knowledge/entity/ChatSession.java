package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("chat_sessions")
public class ChatSession {
    @TableId(type = IdType.AUTO)
    private Long id;

    private String sessionId;

    private String sessionName;

    private String createdBy;

    private String status;

    private Integer messageCount;

    private LocalDateTime createdTime;

    private LocalDateTime lastActiveTime;
}


