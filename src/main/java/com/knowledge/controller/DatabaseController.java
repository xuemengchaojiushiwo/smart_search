package com.knowledge.controller;

import com.knowledge.service.DatabaseService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * 数据库管理控制器
 */
@Slf4j
@RestController
@RequestMapping("/api/database")
@Tag(name = "数据库管理", description = "数据库初始化和清理接口")
public class DatabaseController {

    @Autowired
    private DatabaseService databaseService;

    @Operation(summary = "初始化PostgreSQL数据库", description = "创建所有表结构和初始数据")
    @PostMapping("/init")
    public ResponseEntity<Map<String, Object>> initDatabase() {
        Map<String, Object> result = new HashMap<>();
        try {
            log.info("开始初始化PostgreSQL数据库...");
            databaseService.initPostgreSQLDatabase();
            result.put("success", true);
            result.put("message", "PostgreSQL数据库初始化成功");
            log.info("PostgreSQL数据库初始化完成");
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            log.error("PostgreSQL数据库初始化失败", e);
            result.put("success", false);
            result.put("message", "数据库初始化失败: " + e.getMessage());
            return ResponseEntity.status(500).body(result);
        }
    }

    @Operation(summary = "删除所有表", description = "删除所有表结构（危险操作）")
    @DeleteMapping("/drop-all")
    public ResponseEntity<Map<String, Object>> dropAllTables() {
        Map<String, Object> result = new HashMap<>();
        try {
            log.warn("开始删除所有表...");
            databaseService.dropAllTables();
            result.put("success", true);
            result.put("message", "所有表删除成功");
            log.warn("所有表删除完成");
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            log.error("删除所有表失败", e);
            result.put("success", false);
            result.put("message", "删除表失败: " + e.getMessage());
            return ResponseEntity.status(500).body(result);
        }
    }

    @Operation(summary = "检查数据库状态", description = "检查数据库连接和表结构")
    @GetMapping("/status")
    public ResponseEntity<Map<String, Object>> checkDatabaseStatus() {
        Map<String, Object> result = new HashMap<>();
        try {
            Map<String, Object> status = databaseService.checkDatabaseStatus();
            result.put("success", true);
            result.put("data", status);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            log.error("检查数据库状态失败", e);
            result.put("success", false);
            result.put("message", "检查数据库状态失败: " + e.getMessage());
            return ResponseEntity.status(500).body(result);
        }
    }
}
