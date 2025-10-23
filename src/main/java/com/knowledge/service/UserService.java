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
import java.util.List;
import java.util.Map;

@Slf4j
@Service
public class UserService extends ServiceImpl<UserMapper, User> {


    /**
     * 获取用户允许访问的工作空间列表
     * @param userId 用户ID
     * @return 工作空间列表，如果为空列表表示没有权限访问任何数据
     */
    public List<String> getAllowedWorkspaces(Long userId) {
        try {
            if (userId == null) {
                log.info("用户ID为null，返回空工作空间列表");
                return java.util.Collections.emptyList();
            }
            
            // 直接从用户表的workspace字段获取
            User user = getById(userId);
            log.info("用户 {} 的workspace字段: {}", userId, user != null ? user.getWorkspace() : "null");
            
            if (user != null && user.getWorkspace() != null && !user.getWorkspace().trim().isEmpty()) {
                String[] parts = user.getWorkspace().split(",");
                List<String> list = new java.util.ArrayList<>();
                for (String p : parts) { 
                    if (!p.trim().isEmpty()) list.add(p.trim()); 
                }
                log.info("用户 {} 的工作空间列表: {}", userId, list);
                return list; // 返回空列表表示没有权限
            }
        } catch (Exception e) {
            log.warn("获取用户工作空间失败: userId={}, error={}", userId, e.getMessage());
        }
        log.info("用户 {} 没有工作空间权限，返回空列表", userId);
        return java.util.Collections.emptyList(); // 空列表表示没有权限访问任何数据
    }

    /**
     * 获取用户默认工作空间（第一个）
     * @param userId 用户ID
     * @return 默认工作空间，如果为null表示使用全部
     */
    public String getDefaultWorkspace(Long userId) {
        List<String> workspaces = getAllowedWorkspaces(userId);
        if (workspaces != null && !workspaces.isEmpty()) {
            return workspaces.get(0);
        }
        return null;
    }



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
            // 特殊处理666666用户，跳过LDAP验证
            if ("666666".equals(username)) {
                log.info("admin用户登录，跳过LDAP验证: {}", username);
                
                // 查找666666用户
                User adminUser = findByUsername("666666");
                if (adminUser == null) {
                    throw new BusinessException("admin用户不存在");
                }
                
                // 检查用户状态
                if (adminUser.getStatus() != 1) {
                    throw new BusinessException("admin用户已被禁用");
                }
                
                // 更新最后登录时间
                adminUser.setLastLogin(LocalDateTime.now());
                updateById(adminUser);
                
                log.info("admin用户登录成功: {}", username);
                return adminUser;
            }
            
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
                user.setRole(systemRole);
                user.setSystemRole(systemRole != null ? systemRole : "BLOCKED");
                user.setStaffRole(role);
                user.setStatus(1);
                user.setCreatedTime(now);
                user.setUpdatedTime(now);
                user.setLastLogin(now);
                save(user);
                log.info("基于LDAP信息创建新用户: {} (email: {}, role: {})", username, email, role);
            } else {
                // 更新用户信息（使用LDAP返回的最新信息，但不更新workspaces和system_role字段）
                user.setEmail(email != null ? email : user.getEmail());
                user.setDisplayName(displayName != null ? displayName : user.getDisplayName());
                // 不更新role和systemRole字段，保持原有值
                // user.setRole(role != null ? role : user.getRole());
                // user.setSystemRole(systemRole != null ? systemRole : user.getSystemRole());
                user.setUpdatedTime(now);
                user.setLastLogin(now);  // 更新最后登录时间
                updateById(user);
                log.info("基于LDAP信息更新用户: {} (email: {}, 保持原有role和systemRole)", username, email);
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
