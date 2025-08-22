package com.knowledge.service;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.knowledge.entity.User;
import com.knowledge.exception.BusinessException;
import com.knowledge.mapper.UserMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Slf4j
@Service
public class UserService extends ServiceImpl<UserMapper, User> {



    public User findByUsername(String username) {
        return baseMapper.findByUsername(username);
    }

    public User findByStaffId(String staffId) {
        return baseMapper.findByStaffId(staffId);
    }

    public User findByEmail(String email) {
        return baseMapper.findByEmail(email);
    }

    // 验证用户登录（跳过LDAP验证，默认通过）
    @Transactional
    public User validateUser(String username, String password) {
        try {
            log.info("跳过LDAP验证，默认用户验证通过: {}", username);

            // 先按工号匹配（staffId），找不到再按用户名匹配
            User user = null;
            try { user = findByStaffId(username); } catch (Exception ignore) {}
            if (user == null) {
                user = findByUsername(username);
            }
            if (user == null) {
                // 新用户，创建用户记录
                user = new User();
                user.setUsername(username);
                user.setStaffId(username);
                user.setEmail(username + "@example.com"); // 默认邮箱
                user.setRole("USER"); // 兼容字段
                user.setSystemRole("USER");
                user.setStaffRole("WPB");
                user.setStatus(1);
                user.setCreatedTime(LocalDateTime.now());
                user.setUpdatedTime(LocalDateTime.now());
                save(user);
                log.info("创建新用户 {}", username);
            } else {
                // 更新用户信息
                user.setUpdatedTime(LocalDateTime.now());
                updateById(user);
                log.info("更新用户信息: {}", username);
            }

            if (user.getStatus() != 1) {
                throw new BusinessException("用户已被禁用");
            }

            return user;
        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("用户验证失败: {}", e.getMessage(), e);
            throw new BusinessException("用户验证失败");
        }
    }
}
