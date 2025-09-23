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
import java.util.Map;

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

    @Autowired
    private PythonService pythonService;

    // 验证用户登录（调用Python LDAP验证）
    @Transactional
    public User validateUser(String username, String password) {
        try {
            log.info("调用Python LDAP验证: {}", username);

            // 调用Python LDAP验证接口
            Map<String, Object> ldapResult = pythonService.validateLdapUser(username, password);
            
            if (ldapResult == null || !Boolean.TRUE.equals(ldapResult.get("ok"))) {
                throw new BusinessException("LDAP验证失败");
            }

            // 解析Python返回的用户信息
            @SuppressWarnings("unchecked")
            Map<String, Object> userInfo = (Map<String, Object>) ldapResult.get("user");
            if (userInfo == null) {
                throw new BusinessException("用户信息解析失败");
            }

            String email = (String) userInfo.get("email");
            String displayName = (String) userInfo.get("display_name");
            String role = (String) userInfo.get("role");
            String systemRole = (String) userInfo.get("system_role");
            
            // 先按工号匹配（staffId），找不到再按用户名匹配
            User user = null;
            try { user = findByStaffId(username); } catch (Exception ignore) {}
            if (user == null) {
                user = findByUsername(username);
            }
            
            LocalDateTime now = LocalDateTime.now();
            
            if (user == null) {
                // 新用户，使用LDAP信息创建用户记录
                user = new User();
                user.setUsername(username);
                user.setStaffId(username);
                user.setEmail(email != null ? email : username + "@example.com");
                user.setDisplayName(displayName);
                user.setRole(role != null ? role : "USER");
                user.setSystemRole(systemRole != null ? systemRole : "BLOCKED");
                user.setStaffRole("WPB");
                user.setStatus(1);
                user.setCreatedTime(now);
                user.setUpdatedTime(now);
                user.setLastLogin(now);
                save(user);
                log.info("基于LDAP信息创建新用户: {} (email: {}, role: {})", username, email, role);
            } else {
                // 更新用户信息（使用LDAP返回的最新信息）
                user.setEmail(email != null ? email : user.getEmail());
                user.setDisplayName(displayName != null ? displayName : user.getDisplayName());
                user.setRole(role != null ? role : user.getRole());
                user.setSystemRole(systemRole != null ? systemRole : user.getSystemRole());
                user.setUpdatedTime(now);
                user.setLastLogin(now);  // 更新最后登录时间
                updateById(user);
                log.info("基于LDAP信息更新用户: {} (email: {}, role: {})", username, email, role);
            }

            if (user.getStatus() != 1) {
                throw new BusinessException("用户已被禁用");
            }
            
            // BLOCKED角色可以登录，前端会限制某些功能按钮
            if ("BLOCKED".equals(user.getSystemRole())) {
                log.info("受限用户登录: username={}, staffId={}, email={}, systemRole=BLOCKED", 
                        user.getUsername(), user.getStaffId(), user.getEmail());
            }

            return user;
        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("用户验证失败: {}", e.getMessage(), e);
            throw new BusinessException("用户验证失败: " + e.getMessage());
        }
    }
}
