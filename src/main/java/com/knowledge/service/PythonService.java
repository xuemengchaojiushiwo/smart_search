package com.knowledge.service;

import com.alibaba.fastjson2.JSON;
import com.knowledge.exception.BusinessException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
public class PythonService {
    
    @Value("${python.service.url:http://localhost:8000}")
    private String pythonServiceUrl;
    
    private final RestTemplate restTemplate = new RestTemplate();
    
    /**
     * 调用Python脚本进行LDAP验证
     */
    public Map<String, Object> validateLdapUser(String username, String password) {
        try {
            String url = pythonServiceUrl + "/api/ldap/validate";
            
            Map<String, String> requestBody = new HashMap<>();
            requestBody.put("username", username);
            requestBody.put("password", password);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, String>> request = new HttpEntity<>(requestBody, headers);
            
            ResponseEntity<String> response = restTemplate.postForEntity(url, request, String.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                Map<String, Object> result = JSON.parseObject(response.getBody(), Map.class);
                log.info("LDAP验证成功: {}", username);
                return result;
            } else {
                log.error("LDAP验证失败: {}, 状态码: {}", username, response.getStatusCode());
                throw new BusinessException("LDAP验证失败");
            }
        } catch (Exception e) {
            log.error("调用Python LDAP服务失败: {}", e.getMessage(), e);
            throw new BusinessException("LDAP验证服务不可用");
        }
    }
    
    /**
     * 调用Python服务进行普通对话
     */
    public Map<String, Object> chat(String question, String userId) {
        try {
            String url = pythonServiceUrl + "/api/chat";
            
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("question", question);
            requestBody.put("user_id", userId);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);
            
            ResponseEntity<String> response = restTemplate.postForEntity(url, request, String.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                Map<String, Object> result = JSON.parseObject(response.getBody(), Map.class);
                log.info("普通对话成功: {}", question);
                return result;
            } else {
                log.error("普通对话失败: {}, 状态码: {}", question, response.getStatusCode());
                throw new BusinessException("对话服务调用失败");
            }
        } catch (Exception e) {
            log.error("调用Python对话服务失败: {}", e.getMessage(), e);
            throw new BusinessException("对话服务不可用");
        }
    }
    
    /**
     * 调用Python RAG服务进行智能问答
     */
    public Map<String, Object> chatWithRag(String question, String userId) {
        try {
            String url = pythonServiceUrl + "/api/rag/chat";
            
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("question", question);
            requestBody.put("user_id", userId);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);
            
            ResponseEntity<String> response = restTemplate.postForEntity(url, request, String.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                Map<String, Object> result = JSON.parseObject(response.getBody(), Map.class);
                log.info("RAG对话成功: {}", question);
                return result;
            } else {
                log.error("RAG对话失败: {}, 状态码: {}", question, response.getStatusCode());
                throw new BusinessException("RAG服务调用失败");
            }
        } catch (Exception e) {
            log.error("调用Python RAG服务失败: {}", e.getMessage(), e);
            throw new BusinessException("RAG服务不可用");
        }
    }
    
    /**
     * 调用Python服务处理文档
     */
    public Map<String, Object> processDocument(MultipartFile file, Long knowledgeId, String knowledgeName, 
                                              String description, String tags, String effectiveTime) {
        try {
            String url = pythonServiceUrl + "/api/document/process";
            
            // 构建multipart请求
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);
            
            // 创建multipart body
            org.springframework.core.io.ByteArrayResource fileResource = 
                new org.springframework.core.io.ByteArrayResource(file.getBytes()) {
                    @Override
                    public String getFilename() {
                        return file.getOriginalFilename();
                    }
                };
            
            org.springframework.http.HttpEntity<org.springframework.core.io.Resource> fileEntity = 
                new org.springframework.http.HttpEntity<>(fileResource, headers);
            
            // 构建请求参数
            Map<String, Object> body = new HashMap<>();
            body.put("file", fileEntity);
            body.put("knowledge_id", knowledgeId);
            body.put("knowledge_name", knowledgeName);
            body.put("description", description);
            body.put("tags", tags);
            body.put("effective_time", effectiveTime);
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(body, headers);
            
            ResponseEntity<String> response = restTemplate.postForEntity(url, request, String.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                Map<String, Object> result = JSON.parseObject(response.getBody(), Map.class);
                log.info("文档处理成功: {}", file.getOriginalFilename());
                return result;
            } else {
                log.error("文档处理失败: {}, 状态码: {}", file.getOriginalFilename(), response.getStatusCode());
                throw new BusinessException("文档处理失败");
            }
        } catch (Exception e) {
            log.error("调用Python文档处理服务失败: {}", e.getMessage(), e);
            throw new BusinessException("文档处理服务不可用");
        }
    }
    
    /**
     * 检查Python服务健康状态
     */
    public Map<String, Object> checkHealth() {
        try {
            String url = pythonServiceUrl + "/api/health";
            
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                Map<String, Object> result = JSON.parseObject(response.getBody(), Map.class);
                log.info("Python服务健康检查成功");
                return result;
            } else {
                log.error("Python服务健康检查失败, 状态码: {}", response.getStatusCode());
                throw new BusinessException("Python服务不可用");
            }
        } catch (Exception e) {
            log.error("Python服务健康检查失败: {}", e.getMessage(), e);
            throw new BusinessException("Python服务不可用");
        }
    }
}