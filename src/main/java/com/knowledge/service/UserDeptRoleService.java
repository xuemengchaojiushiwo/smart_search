package com.knowledge.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.knowledge.entity.UserDeptRole;
import com.knowledge.exception.BusinessException;
import com.knowledge.mapper.UserDeptRoleMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class UserDeptRoleService {
    private final UserDeptRoleMapper mapper;

    public List<UserDeptRole> listByUser(Long userId) {
        return mapper.selectList(new LambdaQueryWrapper<UserDeptRole>()
                .eq(UserDeptRole::getUserId, userId));
    }

    public List<UserDeptRole> listByDept(String dept) {
        return mapper.selectList(new LambdaQueryWrapper<UserDeptRole>()
                .eq(UserDeptRole::getDept, dept));
    }

    public UserDeptRole upsert(Long userId, String dept, String role) {
        UserDeptRole existing = mapper.selectOne(new LambdaQueryWrapper<UserDeptRole>()
                .eq(UserDeptRole::getUserId, userId)
                .eq(UserDeptRole::getDept, dept));
        if (existing == null) {
            UserDeptRole rec = new UserDeptRole();
            rec.setUserId(userId);
            rec.setDept(dept);
            rec.setRole(role);
            mapper.insert(rec);
            return rec;
        } else {
            existing.setRole(role);
            mapper.updateById(existing);
            return existing;
        }
    }

    public UserDeptRole updateDept(Long userId, String dept) {
        // 查找用户现有的部门角色记录
        List<UserDeptRole> existingRecords = mapper.selectList(new LambdaQueryWrapper<UserDeptRole>()
                .eq(UserDeptRole::getUserId, userId));
        
        if (existingRecords.isEmpty()) {
            // 如果没有现有记录，创建新的记录，角色默认为REVIEWER
            UserDeptRole newRecord = new UserDeptRole();
            newRecord.setUserId(userId);
            newRecord.setDept(dept);
            newRecord.setRole("REVIEWER"); // 默认角色
            mapper.insert(newRecord);
            return newRecord;
        } else {
            // 如果有现有记录，更新第一个记录的部门
            UserDeptRole firstRecord = existingRecords.get(0);
            firstRecord.setDept(dept);
            mapper.updateById(firstRecord);
            return firstRecord;
        }
    }

    public UserDeptRole updateRole(Long userId, String dept, String role) {
        // 查找指定部门的记录
        UserDeptRole existing = mapper.selectOne(new LambdaQueryWrapper<UserDeptRole>()
                .eq(UserDeptRole::getUserId, userId)
                .eq(UserDeptRole::getDept, dept));
        
        if (existing == null) {
            // 如果没有找到记录，创建新的记录
            UserDeptRole newRecord = new UserDeptRole();
            newRecord.setUserId(userId);
            newRecord.setDept(dept);
            newRecord.setRole(role);
            mapper.insert(newRecord);
            return newRecord;
        } else {
            // 更新现有记录的角色
            existing.setRole(role);
            mapper.updateById(existing);
            return existing;
        }
    }

    public void assertReviewerOfDept(Long userId, String dept) {
        UserDeptRole rec = mapper.selectOne(new LambdaQueryWrapper<UserDeptRole>()
                .eq(UserDeptRole::getUserId, userId)
                .eq(UserDeptRole::getDept, dept));
        if (rec == null || !"REVIEWER".equals(rec.getRole())) {
            throw new BusinessException("无权限：仅本部门reviewer可操作");
        }
    }
}


