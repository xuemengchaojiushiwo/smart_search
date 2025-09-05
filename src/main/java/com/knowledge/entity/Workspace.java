package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("workspaces")
public class Workspace {
    @TableId(type = IdType.AUTO)
    private Long id;
    /** 唯一编码，如 WPB/GPB */
    private String code;
    /** 展示名称，可与code相同 */
    private String name;
    private String description;
    private LocalDateTime createdTime;
}


