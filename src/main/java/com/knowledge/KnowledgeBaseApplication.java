package com.knowledge;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
/**
 TRUNCATE TABLE attachments;
TRUNCATE TABLE chat_feedbacks;
TRUNCATE TABLE chat_messages;
TRUNCATE TABLE chat_sessions;
TRUNCATE TABLE knowledge;
TRUNCATE TABLE knowledge_favorites;
TRUNCATE TABLE knowledge_feedbacks;
TRUNCATE TABLE knowledge_likes;
TRUNCATE TABLE knowledge_versions;
TRUNCATE TABLE knowledge_workspace;
TRUNCATE TABLE search_history;
TRUNCATE TABLE user_dept_role;
TRUNCATE TABLE users;
TRUNCATE TABLE workspaces;
 */
@SpringBootApplication
@MapperScan("com.knowledge.mapper")
public class KnowledgeBaseApplication {

    public static void main(String[] args) {
        SpringApplication.run(KnowledgeBaseApplication.class, args);
    }
} 