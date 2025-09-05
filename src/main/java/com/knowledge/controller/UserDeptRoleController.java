package com.knowledge.controller;

import com.knowledge.entity.UserDeptRole;
import com.knowledge.enums.Department;
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

//     @PutMapping("/{userId}/dept-roles")
//     public UserDeptRole upsert(@PathVariable Long userId, @RequestBody UpdateRoleReq req) {
//         return service.upsert(userId, req.getDept(), req.getRole());
//     }

    @PostMapping("/{userId}/dept")
    public UserDeptRole updateDept(@PathVariable Long userId, @RequestBody UpdateDeptReq req) {
        return service.updateDept(userId, req.getDept());
    }

    @PostMapping("/{userId}/role")
    public UserDeptRole updateRole(@PathVariable Long userId, @RequestBody UpdateRoleOnlyReq req) {
        return service.updateRole(userId, req.getDept(), req.getRole());
    }

    @Data
    public static class UpdateRoleReq {
        private String dept;
        private String role;
    }

    @Data
    public static class UpdateDeptReq {
        private String dept;
    }

    @Data
    public static class UpdateRoleOnlyReq {
        private String dept;
        private String role;
    }
}


