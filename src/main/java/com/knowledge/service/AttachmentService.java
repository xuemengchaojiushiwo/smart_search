package com.knowledge.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.knowledge.entity.Attachment;
import com.knowledge.mapper.AttachmentMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@Slf4j
@Service
public class AttachmentService extends ServiceImpl<AttachmentMapper, Attachment> {
    
    /**
     * 保存文件
     */
    public void saveFiles(Long knowledgeId, MultipartFile[] files, String currentUser) {
        // 实现文件保存逻辑
        log.info("保存文件: knowledgeId={}, fileCount={}", knowledgeId, files != null ? files.length : 0);
    }
    
    /**
     * 带版本管理的文件保存
     */
    public void saveFilesWithVersion(Long knowledgeId, Long versionId, Integer versionNumber, 
                                   MultipartFile[] files, String currentUser, String changeReason) {
        // 实现带版本管理的文件保存逻辑
        log.info("保存文件（带版本）: knowledgeId={}, versionId={}, fileCount={}", knowledgeId, versionId, files != null ? files.length : 0);
    }
    
    /**
     * 根据知识ID获取附件列表
     */
    public List<Attachment> getByKnowledgeId(Long knowledgeId) {
        LambdaQueryWrapper<Attachment> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Attachment::getKnowledgeId, knowledgeId);
        wrapper.eq(Attachment::getDeleted, 0);
        return list(wrapper);
    }
}
