package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("search_history")
public class SearchHistory {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private Long userId;

    private String query;
    
    private LocalDateTime searchTime;
    
    private Integer resultCount;
    
    @TableLogic
    private Integer deleted;
}
