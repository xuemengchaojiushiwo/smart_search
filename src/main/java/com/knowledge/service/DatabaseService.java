package com.knowledge.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.ClassPathResource;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.sql.DataSource;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;

/**
 * 数据库管理服务
 */
@Slf4j
@Service
public class DatabaseService {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Autowired
    private DataSource dataSource;

    /**
     * 初始化PostgreSQL数据库
     */
    @Transactional
    public void initPostgreSQLDatabase() {
        log.info("开始执行PostgreSQL数据库初始化...");
        
        try {
            // 读取SQL脚本
            String sqlScript = readSQLScript("db/init_postgresql_fixed.sql");
            
            // 分割SQL语句（按分号分割，但要注意字符串中的分号）
            List<String> statements = splitSQLStatements(sqlScript);
            
            // 执行每个SQL语句
            for (String statement : statements) {
                statement = statement.trim();
                if (statement.isEmpty() || statement.startsWith("--") || statement.startsWith("\\")) {
                    continue; // 跳过空行、注释和psql命令
                }
                
                try {
                    log.debug("执行SQL: {}", statement.substring(0, Math.min(100, statement.length())) + "...");
                    jdbcTemplate.execute(statement);
                } catch (Exception e) {
                    log.warn("执行SQL语句失败，可能已存在: {}", e.getMessage());
                    // 继续执行其他语句
                }
            }
            
            log.info("PostgreSQL数据库初始化完成");
            
        } catch (Exception e) {
            log.error("PostgreSQL数据库初始化失败", e);
            throw new RuntimeException("数据库初始化失败: " + e.getMessage(), e);
        }
    }

    /**
     * 删除所有表
     */
    @Transactional
    public void dropAllTables() {
        log.warn("开始删除所有表...");
        
        try {
            // 获取所有表名
            List<String> tables = getAllTableNames();
            
            if (tables.isEmpty()) {
                log.info("没有找到任何表");
                return;
            }
            
            // 删除外键约束
            disableForeignKeyChecks();
            
            // 删除所有表
            for (String table : tables) {
                try {
                    log.info("删除表: {}", table);
                    jdbcTemplate.execute("DROP TABLE IF EXISTS " + table + " CASCADE");
                } catch (Exception e) {
                    log.warn("删除表 {} 失败: {}", table, e.getMessage());
                }
            }
            
            // 重新启用外键约束
            enableForeignKeyChecks();
            
            log.warn("所有表删除完成");
            
        } catch (Exception e) {
            log.error("删除所有表失败", e);
            throw new RuntimeException("删除表失败: " + e.getMessage(), e);
        }
    }

    /**
     * 检查数据库状态
     */
    public Map<String, Object> checkDatabaseStatus() {
        Map<String, Object> status = new HashMap<>();
        
        try {
            // 检查数据库连接
            status.put("connection", "正常");
            
            // 获取数据库信息
            String dbName = jdbcTemplate.queryForObject("SELECT current_database()", String.class);
            String dbVersion = jdbcTemplate.queryForObject("SELECT version()", String.class);
            
            status.put("database", dbName);
            status.put("version", dbVersion);
            
            // 获取表列表
            List<String> tables = getAllTableNames();
            status.put("tables", tables);
            status.put("tableCount", tables.size());
            
            // 检查关键表是否存在
            List<String> keyTables = Arrays.asList("users", "knowledge", "knowledge_workspace", "attachments");
            Map<String, Boolean> keyTableStatus = new HashMap<>();
            for (String table : keyTables) {
                keyTableStatus.put(table, tables.contains(table));
            }
            status.put("keyTables", keyTableStatus);
            
            // 检查数据量
            Map<String, Long> tableCounts = new HashMap<>();
            for (String table : tables) {
                try {
                    Long count = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM " + table, Long.class);
                    tableCounts.put(table, count);
                } catch (Exception e) {
                    tableCounts.put(table, -1L); // 表示查询失败
                }
            }
            status.put("tableCounts", tableCounts);
            
        } catch (Exception e) {
            log.error("检查数据库状态失败", e);
            status.put("connection", "异常");
            status.put("error", e.getMessage());
        }
        
        return status;
    }

    /**
     * 读取SQL脚本文件
     */
    private String readSQLScript(String scriptPath) throws Exception {
        ClassPathResource resource = new ClassPathResource(scriptPath);
        
        StringBuilder sqlScript = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(resource.getInputStream(), StandardCharsets.UTF_8))) {
            
            String line;
            while ((line = reader.readLine()) != null) {
                sqlScript.append(line).append("\n");
            }
        }
        
        return sqlScript.toString();
    }

    /**
     * 分割SQL语句
     */
    private List<String> splitSQLStatements(String sqlScript) {
        List<String> statements = new ArrayList<>();
        StringBuilder currentStatement = new StringBuilder();
        boolean inString = false;
        char stringChar = 0;
        
        for (int i = 0; i < sqlScript.length(); i++) {
            char c = sqlScript.charAt(i);
            
            if (!inString && (c == '\'' || c == '"')) {
                inString = true;
                stringChar = c;
            } else if (inString && c == stringChar) {
                inString = false;
            } else if (!inString && c == ';') {
                String statement = currentStatement.toString().trim();
                if (!statement.isEmpty()) {
                    statements.add(statement);
                }
                currentStatement = new StringBuilder();
                continue;
            }
            
            currentStatement.append(c);
        }
        
        // 添加最后一个语句
        String lastStatement = currentStatement.toString().trim();
        if (!lastStatement.isEmpty()) {
            statements.add(lastStatement);
        }
        
        return statements;
    }

    /**
     * 获取所有表名
     */
    private List<String> getAllTableNames() {
        try {
            return jdbcTemplate.queryForList(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public'", 
                String.class
            );
        } catch (Exception e) {
            log.error("获取表名列表失败", e);
            return new ArrayList<>();
        }
    }

    /**
     * 禁用外键检查（PostgreSQL不需要，但保留接口）
     */
    private void disableForeignKeyChecks() {
        // PostgreSQL 在 DROP TABLE CASCADE 时会自动处理外键约束
        log.debug("PostgreSQL 使用 CASCADE 自动处理外键约束");
    }

    /**
     * 启用外键检查（PostgreSQL不需要，但保留接口）
     */
    private void enableForeignKeyChecks() {
        // PostgreSQL 不需要手动启用外键检查
        log.debug("PostgreSQL 外键约束已自动处理");
    }
}
