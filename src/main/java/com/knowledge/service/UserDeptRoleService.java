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

    public void assertReviewerOfDept(Long userId, String dept) {
        UserDeptRole rec = mapper.selectOne(new LambdaQueryWrapper<UserDeptRole>()
                .eq(UserDeptRole::getUserId, userId)
                .eq(UserDeptRole::getDept, dept));
        if (rec == null || !"REVIEWER".equals(rec.getRole())) {
            throw new BusinessException("无权限：仅本部门reviewer可操作");
        }
    }
}


