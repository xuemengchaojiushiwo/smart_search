package com.knowledge.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.knowledge.entity.Attachment;
import com.knowledge.mapper.AttachmentMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.time.LocalDateTime;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;
import java.security.MessageDigest;
import com.knowledge.exception.BusinessException;
import org.springframework.beans.factory.annotation.Value;

@Slf4j
@Service
public class AttachmentService extends ServiceImpl<AttachmentMapper, Attachment> {
    @Value("${app.upload-dir:uploads}")
    private String baseUploadDir;
    
    /**
     * 保存文件
     */
    public void saveFiles(Long knowledgeId, MultipartFile[] files, String currentUser) {
        log.info("保存文件: knowledgeId={}, fileCount={}", knowledgeId, files != null ? files.length : 0);
        if (files == null || files.length == 0) {
            throw new BusinessException("未选择任何文件");
        }
        int savedCount = 0;
        for (MultipartFile file : files) {
            if (file == null || file.isEmpty()) {
                continue;
            }
            try {
                // 计算文件hash，用于去重
                String fileHash = computeSha256(file.getBytes());
                // 去重：同一知识下已存在相同hash则禁止重复上传
                com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<Attachment> dupWrapper = new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<>();
                dupWrapper.eq(Attachment::getKnowledgeId, knowledgeId)
                        .eq(Attachment::getFileHash, fileHash)
                        .eq(Attachment::getDeleted, 0);
                long dupCount = count(dupWrapper);
                if (dupCount > 0) {
                    throw new BusinessException("相同文件已存在，禁止重复上传");
                }

                // 物理保存到配置的 uploads 目录（支持绝对/相对路径）
                String originalName = file.getOriginalFilename();
                String safeName = (originalName != null && !originalName.isEmpty()) ? originalName : ("file-" + UUID.randomUUID());
                String uniqueName = UUID.randomUUID().toString().replace("-", "") + "_" + safeName;
                Path uploadDir = Paths.get(baseUploadDir).toAbsolutePath().normalize();
                Files.createDirectories(uploadDir);
                Path target = uploadDir.resolve(uniqueName);
                Files.createDirectories(target.getParent());
                try {
                    file.transferTo(target.toFile());
                } catch (Exception io) {
                    throw new BusinessException("保存文件到磁盘失败: " + io.getMessage());
                }

                // 记录到数据库
                Attachment attachment = new Attachment();
                attachment.setKnowledgeId(knowledgeId);
                attachment.setFileName(safeName);
                attachment.setFilePath(target.toAbsolutePath().toString());
                attachment.setFileSize(file.getSize());
                attachment.setFileType(file.getContentType());
                attachment.setUploadTime(LocalDateTime.now());
                attachment.setDownloadCount(0);
                attachment.setDeleted(0);
                attachment.setFileHash(fileHash);
                boolean ok = save(attachment);
                if (!ok) {
                    throw new BusinessException("保存附件记录失败");
                }
                log.info("附件保存成功: knowledgeId={}, attachmentId={}, name={}", knowledgeId, attachment.getId(), safeName);
                savedCount++;
            } catch (Exception e) {
                log.error("保存附件失败: knowledgeId={}, fileName={}, error={}", knowledgeId, file != null ? file.getOriginalFilename() : "", e.getMessage(), e);
                if (e instanceof BusinessException) {
                    throw (BusinessException) e;
                }
                throw new BusinessException("保存附件失败: " + e.getMessage());
            }
        }
        if (savedCount == 0) {
            throw new BusinessException("未保存任何附件");
        }
    }
    
    /**
     * 带版本管理的文件保存
     */
    public void saveFilesWithVersion(Long knowledgeId, Long versionId, Integer versionNumber, 
                                   MultipartFile[] files, String currentUser, String changeReason) {
        log.info("保存文件（带版本）: knowledgeId={}, versionId={}, fileCount={}", knowledgeId, versionId, files != null ? files.length : 0);
        if (files == null || files.length == 0) {
            throw new BusinessException("未选择任何文件");
        }
        int savedCount = 0;
        for (MultipartFile file : files) {
            if (file == null || file.isEmpty()) {
                continue;
            }
            try {
                String fileHash = computeSha256(file.getBytes());
                com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<Attachment> dupWrapper = new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<>();
                dupWrapper.eq(Attachment::getKnowledgeId, knowledgeId)
                        .eq(Attachment::getFileHash, fileHash)
                        .eq(Attachment::getDeleted, 0);
                long dupCount = count(dupWrapper);
                if (dupCount > 0) {
                    throw new BusinessException("相同文件已存在，禁止重复上传");
                }

                String originalName = file.getOriginalFilename();
                String safeName = (originalName != null && !originalName.isEmpty()) ? originalName : ("file-" + UUID.randomUUID());
                String uniqueName = UUID.randomUUID().toString().replace("-", "") + "_" + safeName;
                Path uploadDir = Paths.get(baseUploadDir).toAbsolutePath().normalize();
                Files.createDirectories(uploadDir);
                Path target = uploadDir.resolve(uniqueName);
                Files.createDirectories(target.getParent());
                try {
                    file.transferTo(target.toFile());
                } catch (Exception io) {
                    throw new BusinessException("保存文件到磁盘失败: " + io.getMessage());
                }

                Attachment attachment = new Attachment();
                attachment.setKnowledgeId(knowledgeId);
                attachment.setFileName(safeName);
                attachment.setFilePath(target.toAbsolutePath().toString());
                attachment.setFileSize(file.getSize());
                attachment.setFileType(file.getContentType());
                attachment.setUploadTime(LocalDateTime.now());
                attachment.setDownloadCount(0);
                attachment.setDeleted(0);
                attachment.setVersionId(versionId);
                attachment.setVersionNumber(versionNumber);
                attachment.setFileHash(fileHash);
                boolean ok = save(attachment);
                if (!ok) {
                    throw new BusinessException("保存附件记录失败");
                }
                log.info("附件保存成功（带版本）: knowledgeId={}, versionId={}, attachmentId={}, name={}", knowledgeId, versionId, attachment.getId(), safeName);
                savedCount++;
            } catch (Exception e) {
                log.error("保存附件（带版本）失败: knowledgeId={}, fileName={}, error={}", knowledgeId, file != null ? file.getOriginalFilename() : "", e.getMessage(), e);
                if (e instanceof BusinessException) {
                    throw (BusinessException) e;
                }
                throw new BusinessException("保存附件失败: " + e.getMessage());
            }
        }
        if (savedCount == 0) {
            throw new BusinessException("未保存任何附件");
        }
    }

    private String computeSha256(byte[] data) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] hash = digest.digest(data);
        StringBuilder sb = new StringBuilder();
        for (byte b : hash) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
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

    /**
     * 根据知识ID与文件名获取最新一条附件记录
     */
    public Attachment findByKnowledgeIdAndFileName(Long knowledgeId, String fileName) {
        if (knowledgeId == null || fileName == null || fileName.isEmpty()) {
            return null;
        }
        LambdaQueryWrapper<Attachment> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Attachment::getKnowledgeId, knowledgeId)
                .eq(Attachment::getFileName, fileName)
                .eq(Attachment::getDeleted, 0)
                .orderByDesc(Attachment::getUploadTime)
                .last("LIMIT 1");
        return getOne(wrapper, false);
    }
}
