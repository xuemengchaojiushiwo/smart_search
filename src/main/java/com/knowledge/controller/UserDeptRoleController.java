package com.knowledge.controller;

import com.knowledge.entity.UserDeptRole;
import com.knowledge.enums.Department;
import com.knowledge.enums.DeptRole;
import com.knowledge.service.UserDeptRoleService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserDeptRoleController {
    private final UserDeptRoleService service;

    @GetMapping("/departments")
    public Department[] listDepartments() {
        return Department.values();
    }

    @GetMapping("/{userId}/dept-roles")
    public List<UserDeptRole> list(@PathVariable Long userId) {
        return service.listByUser(userId);
    }

    @GetMapping
    public List<UserDeptRole> listByDept(@RequestParam(required = false) String dept) {
        if (dept == null) return service.listByDept("WPB"); // 简单默认可改
        return service.listByDept(dept);
    }

    @PutMapping("/{userId}/dept-roles")
    public UserDeptRole upsert(@PathVariable Long userId, @RequestBody UpdateRoleReq req) {
        return service.upsert(userId, req.getDept(), req.getRole());
    }

    @Data
    public static class UpdateRoleReq {
        private String dept;
        private String role;
    }
}


