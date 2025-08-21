package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("user_dept_role")
public class UserDeptRole {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long userId;
    /** 部门，保存为字符串，如 WPB/GPB */
    private String dept;
    /** 角色，保存为字符串，如 REVIEWER/BLOCKER */
    private String role;
}


