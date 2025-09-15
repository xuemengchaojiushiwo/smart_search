package com.knowledge.util;

import com.knowledge.entity.User;
import com.knowledge.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

@Component
public class SecurityUtils {
    
    private static UserService userService;
    
    @Autowired
    public void setUserService(UserService userService) {
        SecurityUtils.userService = userService;
    }
    
    /**
     * 获取当前登录用户名
     */
    public static String getCurrentUsername() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null && authentication.isAuthenticated()) {
            return authentication.getName();
        }
        return null;
    }
    
    /**
     * 获取当前登录用户角色
     */
    public static String getCurrentUserRole() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null && authentication.isAuthenticated() && !authentication.getAuthorities().isEmpty()) {
            return authentication.getAuthorities().iterator().next().getAuthority().replace("ROLE_", "");
        }
        return null;
    }
    
    /**
     * 检查当前用户是否已认证
     */
    public static boolean isAuthenticated() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        return authentication != null && authentication.isAuthenticated() && 
               !"anonymousUser".equals(authentication.getName());
    }
    
    /**
     * 获取当前登录用户ID（数据库主键）
     */
    public static Long getCurrentUserId() {
        String username = getCurrentUsername();
        if (username != null && userService != null) {
            try {
                User user = userService.findByUsername(username);
                return user != null ? user.getId() : null;
            } catch (Exception e) {
                // 如果按用户名找不到，尝试按工号查找
                try {
                    User user = userService.findByStaffId(username);
                    return user != null ? user.getId() : null;
                } catch (Exception ex) {
                    return null;
                }
            }
        }
        return null;
    }
    
    /**
     * 获取当前登录用户工号（用于搜索历史记录）
     */
    public static String getCurrentUserStaffId() {
        String username = getCurrentUsername();
        if (username != null && userService != null) {
            try {
                User user = userService.findByUsername(username);
                if (user != null) {
                    return user.getStaffId();
                }
            } catch (Exception e) {
                // 如果按用户名找不到，尝试按工号查找
                try {
                    User user = userService.findByStaffId(username);
                    if (user != null) {
                        return user.getStaffId();
                    }
                } catch (Exception ex) {
                    return null;
                }
            }
        }
        return null;
    }
}

