package com.knowledge.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.knowledge.dto.KnowledgeDTO;
import com.knowledge.entity.Attachment;
import com.knowledge.entity.Knowledge;
import com.knowledge.entity.KnowledgeVersion;
import com.knowledge.exception.BusinessException;
import com.knowledge.mapper.KnowledgeMapper;
import com.knowledge.vo.KnowledgeVO;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
public class KnowledgeService {
    
    @Autowired
    private KnowledgeMapper knowledgeMapper;
    
    @Autowired
    private KnowledgeVersionService knowledgeVersionService;
    
    @Autowired
    private AttachmentService attachmentService;
    
    @Autowired
    private CategoryService categoryService;
    
    @Autowired
    private PythonService pythonService;
    
    @Autowired
    private ElasticsearchService elasticsearchService;
    
    /**
     * 创建知识
     */
    @Transactional
    public Knowledge createKnowledge(KnowledgeDTO dto, String currentUser) {
        Knowledge knowledge = new Knowledge();
        BeanUtils.copyProperties(dto, knowledge);
        knowledge.setCreatedBy(currentUser);
        knowledge.setUpdatedBy(currentUser);
        knowledge.setStatus(1);
        knowledge.setSearchCount(0);
        knowledge.setDownloadCount(0);
        
        knowledgeMapper.insert(knowledge);
        
        // 索引到ES
        elasticsearchService.indexKnowledge(knowledge, null);
        
        log.info("知识创建成功: ID={}, 名称={}", knowledge.getId(), knowledge.getName());
        return knowledge;
    }
    
    /**
     * 创建知识（支持文件上传）
     */
    @Transactional
    public Knowledge createKnowledgeWithFiles(KnowledgeDTO dto, MultipartFile[] files, String currentUser) {
        // 创建知识
        Knowledge knowledge = createKnowledge(dto, currentUser);
        
        // 保存附件
        if (files != null && files.length > 0) {
            attachmentService.saveFiles(knowledge.getId(), files, currentUser);
        }
        
        // 索引到ES（包含附件信息）
        List<Attachment> attachments = attachmentService.getByKnowledgeId(knowledge.getId());
        elasticsearchService.indexKnowledge(knowledge, attachments);
        
        log.info("知识创建成功（含文件）: ID={}, 名称={}, 文件数={}", knowledge.getId(), knowledge.getName(), files != null ? files.length : 0);
        return knowledge;
    }
    
    /**
     * 更新知识
     */
    @Transactional
    public Knowledge updateKnowledge(Long id, KnowledgeDTO dto, String currentUser) {
        Knowledge existingKnowledge = getById(id);
        if (existingKnowledge == null) {
            throw new BusinessException("知识不存在");
        }
        
        // 保存版本
        KnowledgeVersion version = saveVersion(existingKnowledge, "UPDATE", dto.getChangeReason(), currentUser);
        
        // 更新知识
        BeanUtils.copyProperties(dto, existingKnowledge);
        existingKnowledge.setUpdatedBy(currentUser);
        existingKnowledge.setUpdatedTime(LocalDateTime.now());
        
        knowledgeMapper.updateById(existingKnowledge);
        
        // 更新ES索引
        List<Attachment> attachments = attachmentService.getByKnowledgeId(id);
        elasticsearchService.updateKnowledge(existingKnowledge, attachments);
        
        log.info("知识更新成功: ID={}, 名称={}", id, existingKnowledge.getName());
        return existingKnowledge;
    }
    
    /**
     * 删除知识
     */
    @Transactional
    public void deleteKnowledge(Long id, String currentUser) {
        Knowledge knowledge = getById(id);
        if (knowledge == null) {
            throw new BusinessException("知识不存在");
        }
        
        // 逻辑删除
        knowledge.setDeleted(1);
        knowledge.setUpdatedBy(currentUser);
        knowledge.setUpdatedTime(LocalDateTime.now());
        knowledgeMapper.updateById(knowledge);
        
        // 从ES删除
        elasticsearchService.deleteKnowledge(id);
        
        log.info("知识删除成功: ID={}, 名称={}", id, knowledge.getName());
    }
    
    /**
     * 获取知识列表
     */
    public IPage<KnowledgeVO> getKnowledgeList(int page, int size) {
        Page<Knowledge> pageParam = new Page<>(page, size);
        LambdaQueryWrapper<Knowledge> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Knowledge::getDeleted, 0);
        wrapper.orderByDesc(Knowledge::getCreatedTime);
        
        IPage<Knowledge> knowledgePage = knowledgeMapper.selectPage(pageParam, wrapper);
        
        return knowledgePage.convert(this::convertToVO);
    }
    
    /**
     * 根据类目获取知识
     */
    public IPage<KnowledgeVO> getKnowledgeByCategory(Long categoryId, int page, int size) {
        Page<Knowledge> pageParam = new Page<>(page, size);
        LambdaQueryWrapper<Knowledge> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Knowledge::getDeleted, 0);
        wrapper.eq(Knowledge::getCategoryId, categoryId);
        wrapper.orderByDesc(Knowledge::getCreatedTime);
        
        IPage<Knowledge> knowledgePage = knowledgeMapper.selectPage(pageParam, wrapper);
        
        return knowledgePage.convert(this::convertToVO);
    }
    
    /**
     * 搜索知识
     */
    public IPage<KnowledgeVO> searchKnowledge(String query, int page, int size) {
        // 仅使用ES搜索，失败直接抛出异常
        List<com.knowledge.vo.ElasticsearchResultVO> esResults = elasticsearchService
            .searchKnowledge(query, (page - 1) * size, size);

        List<KnowledgeVO> vos = esResults.stream()
            .map(esResult -> {
                KnowledgeVO vo = new KnowledgeVO();
                vo.setId(esResult.getId());
                vo.setName(esResult.getTitle());
                vo.setDescription(esResult.getContent());
                if (esResult.getCategoryId() != null) {
                    try {
                        vo.setCategoryId(Long.valueOf(esResult.getCategoryId()));
                    } catch (NumberFormatException e) {
                        log.warn("无法转换categoryId: {}", esResult.getCategoryId());
                    }
                }
                if (esResult.getTags() != null) {
                    vo.setTags(java.util.Arrays.asList(esResult.getTags().split(",")));
                }
                vo.setCreatedBy(esResult.getAuthor());
                return vo;
            })
            .collect(Collectors.toList());

        Page<KnowledgeVO> result = new Page<>(page, size);
        result.setRecords(vos);
        result.setTotal(elasticsearchService.getSearchCount(query));
        return result;
    }
    
    /**
     * 获取热门知识
     */
    public List<KnowledgeVO> getPopularKnowledge(int limit) {
        LambdaQueryWrapper<Knowledge> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Knowledge::getDeleted, 0);
        wrapper.orderByDesc(Knowledge::getSearchCount);
        wrapper.last("LIMIT " + limit);
        
        List<Knowledge> knowledges = knowledgeMapper.selectList(wrapper);
        return knowledges.stream().map(this::convertToVO).collect(Collectors.toList());
    }
    
    /**
     * 获取最新知识
     */
    public List<KnowledgeVO> getLatestKnowledge(int limit) {
        LambdaQueryWrapper<Knowledge> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Knowledge::getDeleted, 0);
        wrapper.orderByDesc(Knowledge::getCreatedTime);
        wrapper.last("LIMIT " + limit);
        
        List<Knowledge> knowledges = knowledgeMapper.selectList(wrapper);
        return knowledges.stream().map(this::convertToVO).collect(Collectors.toList());
    }
    
    /**
     * 获取最热资料（根据下载数量倒序）
     */
    public List<KnowledgeVO> getHotDownloads(int limit) {
        LambdaQueryWrapper<Knowledge> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Knowledge::getDeleted, 0);
        wrapper.orderByDesc(Knowledge::getDownloadCount);
        wrapper.orderByDesc(Knowledge::getSearchCount); // 下载数相同时按搜索数排序
        wrapper.last("LIMIT " + limit);
        
        List<Knowledge> knowledges = knowledgeMapper.selectList(wrapper);
        return knowledges.stream().map(this::convertToVO).collect(Collectors.toList());
    }
    
    /**
     * 增加搜索次数
     */
    public void incrementSearchCount(Long id) {
        Knowledge knowledge = getById(id);
        if (knowledge != null) {
            knowledge.setSearchCount(knowledge.getSearchCount() + 1);
            knowledgeMapper.updateById(knowledge);
        }
    }
    
    /**
     * 根据ID获取知识
     */
    public Knowledge getById(Long id) {
        LambdaQueryWrapper<Knowledge> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Knowledge::getId, id);
        wrapper.eq(Knowledge::getDeleted, 0);
        return knowledgeMapper.selectOne(wrapper);
    }
    
    /**
     * 转换为VO
     */
    private KnowledgeVO convertToVO(Knowledge knowledge) {
        KnowledgeVO vo = new KnowledgeVO();
        BeanUtils.copyProperties(knowledge, vo);
        return vo;
    }
    
    /**
     * 保存版本
     */
    private KnowledgeVersion saveVersion(Knowledge knowledge, String changeType, String changeReason, String currentUser) {
        KnowledgeVersion version = new KnowledgeVersion();
        BeanUtils.copyProperties(knowledge, version);
        version.setKnowledgeId(knowledge.getId());
        version.setCreatedBy(currentUser);
        version.setChangeReason(changeReason);
        
        // 获取版本号
        LambdaQueryWrapper<KnowledgeVersion> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(KnowledgeVersion::getKnowledgeId, knowledge.getId());
        wrapper.orderByDesc(KnowledgeVersion::getVersionNumber);
        wrapper.last("LIMIT 1");
        KnowledgeVersion lastVersion = knowledgeVersionService.getOne(wrapper);
        
        if (lastVersion != null) {
            version.setVersionNumber(lastVersion.getVersionNumber() + 1);
        } else {
            version.setVersionNumber(1);
        }
        
        knowledgeVersionService.save(version);
        return version;
    }
    
    /**
     * 处理知识文档并存入ES
     */
    @Transactional
    public Map<String, Object> processKnowledgeDocument(MultipartFile file, Long knowledgeId, String currentUser) {
        try {
            // 获取知识信息
            Knowledge knowledge = getById(knowledgeId);
            if (knowledge == null) {
                throw new BusinessException("知识不存在");
            }
            
            // 调用Python服务处理文档
            String effectiveTime = null;
            if (knowledge.getEffectiveStartTime() != null || knowledge.getEffectiveEndTime() != null) {
                String startTime = knowledge.getEffectiveStartTime() != null ? 
                    knowledge.getEffectiveStartTime().toString() : "未设置";
                String endTime = knowledge.getEffectiveEndTime() != null ? 
                    knowledge.getEffectiveEndTime().toString() : "未设置";
                effectiveTime = startTime + " - " + endTime;
            }
            
            Map<String, Object> result = pythonService.processDocument(
                file,
                knowledgeId,
                knowledge.getName(),
                knowledge.getDescription(),
                knowledge.getTags(),
                effectiveTime
            );
            
            log.info("知识文档处理成功: knowledgeId={}, fileName={}", knowledgeId, file.getOriginalFilename());
            return result;
            
        } catch (Exception e) {
            log.error("知识文档处理失败: knowledgeId={}, error={}", knowledgeId, e.getMessage(), e);
            throw new BusinessException("文档处理失败: " + e.getMessage());
        }
    }
    
    /**
     * 处理多个知识文档并存入ES
     */
    @Transactional
    public Map<String, Object> processKnowledgeDocuments(MultipartFile[] files, Long knowledgeId, String currentUser) {
        try {
            // 获取知识信息
            Knowledge knowledge = getById(knowledgeId);
            if (knowledge == null) {
                throw new BusinessException("知识不存在");
            }
            
            // 记录版本
            KnowledgeVersion version = saveVersion(knowledge, "UPDATE", "上传新文档", currentUser);
            
            // 保存附件（带版本管理）
            attachmentService.saveFilesWithVersion(knowledgeId, version.getId(), version.getVersionNumber(), 
                                                files, currentUser, "上传新文档");
            
            // 处理每个文档
            Map<String, Object> result = new java.util.HashMap<>();
            result.put("processedFiles", files.length);
            result.put("knowledgeId", knowledgeId);
            result.put("versionId", version.getId());
            result.put("versionNumber", version.getVersionNumber());
            result.put("message", "成功处理 " + files.length + " 个文档");
            
            log.info("知识文档处理成功: knowledgeId={}, fileCount={}, versionId={}", knowledgeId, files.length, version.getId());
            return result;
            
        } catch (Exception e) {
            log.error("知识文档处理失败: knowledgeId={}, error={}", knowledgeId, e.getMessage(), e);
            throw new BusinessException("文档处理失败: " + e.getMessage());
        }
    }
    
    /**
     * 根据知识ID获取附件列表
     */
    public List<Attachment> getAttachmentsByKnowledgeId(Long knowledgeId) {
        return attachmentService.getByKnowledgeId(knowledgeId);
    }
} 
