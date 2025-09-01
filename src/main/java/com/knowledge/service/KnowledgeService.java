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
import com.knowledge.vo.AttachmentVO;
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
    
    // 类目模块已移除
    
    @Autowired
    private PythonService pythonService;
    
    @Autowired
    private ElasticsearchService elasticsearchService;

    @Autowired
    private KnowledgeWorkspaceService knowledgeWorkspaceService;
    
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
        // 绑定工作空间（多对多）
        knowledgeWorkspaceService.replaceBindings(knowledge.getId(), dto.getWorkspaces());
        
        // 索引到ES（含workspace）
        java.util.List<String> workspaces = knowledgeWorkspaceService.listWorkspaces(knowledge.getId());
        elasticsearchService.indexKnowledge(knowledge, null, workspaces);
        
        log.info("知识创建成功: ID={}, 名称={}", knowledge.getId(), knowledge.getName());
        return knowledge;
    }
    
    // 原 createKnowledgeWithFiles 已移除。请使用 /api/knowledge/{id}/document 进行文档上传。
    
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
        // 记录版本（目前不使用返回值）
        saveVersion(existingKnowledge, "UPDATE", dto.getChangeReason(), currentUser);
        
        // 更新知识
        BeanUtils.copyProperties(dto, existingKnowledge);
        existingKnowledge.setUpdatedBy(currentUser);
        existingKnowledge.setUpdatedTime(LocalDateTime.now());
        
        knowledgeMapper.updateById(existingKnowledge);
        // 更新工作空间绑定
        knowledgeWorkspaceService.replaceBindings(id, dto.getWorkspaces());
        
        // 更新ES索引
        List<Attachment> attachments = attachmentService.getByKnowledgeId(id);
        java.util.List<String> workspaces = knowledgeWorkspaceService.listWorkspaces(id);
        elasticsearchService.updateKnowledge(existingKnowledge, attachments, workspaces);
        
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
     * 软删除知识对应的附件（DB置 deleted=1），并从ES中删除关联的chunks
     */
    @Transactional
    public void softDeleteAttachment(Long knowledgeId, Long attachmentId, String currentUser) {
        com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<Attachment> wrapper = new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<>();
        wrapper.eq(Attachment::getId, attachmentId)
               .eq(Attachment::getKnowledgeId, knowledgeId)
               .eq(Attachment::getDeleted, 0);
        Attachment attachment = attachmentService.getOne(wrapper);
        if (attachment == null) {
            throw new BusinessException("附件不存在或已删除");
        }

        // DB软删除
        attachment.setDeleted(1);
        attachmentService.updateById(attachment);

        // ES中删除该附件对应的chunks（按 knowledge_id + source_file 匹配）
        try {
            elasticsearchService.deleteChunksByKnowledgeAndFile(knowledgeId, attachment.getFileName());
        } catch (Exception e) {
            log.warn("ES删除附件相关chunks失败: knowledgeId={}, fileName={}, error={}", knowledgeId, attachment.getFileName(), e.getMessage());
        }

        log.info("附件软删除成功: knowledgeId={}, attachmentId={}", knowledgeId, attachmentId);
    }
    
    /**
     * 获取知识列表
     */
    public IPage<KnowledgeVO> getKnowledgeList(int page, int size) {
        Page<Knowledge> pageParam = new Page<>(page, size);
        LambdaQueryWrapper<Knowledge> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Knowledge::getDeleted, 0);
        wrapper.orderByDesc(Knowledge::getUpdatedTime);
        
        IPage<Knowledge> knowledgePage = knowledgeMapper.selectPage(pageParam, wrapper);
        
        return knowledgePage.convert(this::convertToVO);
    }

    public IPage<KnowledgeVO> getKnowledgeListFiltered(int page, int size, java.util.List<String> allowedWorkspaces) {
        if (allowedWorkspaces == null || allowedWorkspaces.isEmpty()) {
            return getKnowledgeList(page, size);
        }
        Page<Knowledge> pageParam = new Page<>(page, size);
        java.util.Set<Long> ids = knowledgeWorkspaceService.listKnowledgeIdsByWorkspaces(allowedWorkspaces);
        if (ids.isEmpty()) {
            Page<KnowledgeVO> empty = new Page<>(page, size);
            empty.setTotal(0);
            empty.setRecords(java.util.Collections.emptyList());
            return empty;
        }
        LambdaQueryWrapper<Knowledge> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Knowledge::getDeleted, 0).in(Knowledge::getId, ids).orderByDesc(Knowledge::getUpdatedTime);
        IPage<Knowledge> knowledgePage = knowledgeMapper.selectPage(pageParam, wrapper);
        return knowledgePage.convert(this::convertToVO);
    }
    
    /**
     * 获取某个父知识下的直接子节点
     */
    public IPage<KnowledgeVO> getChildren(Long parentId, int page, int size) {
        Page<Knowledge> pageParam = new Page<>(page, size);
        LambdaQueryWrapper<Knowledge> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Knowledge::getDeleted, 0);
        if (parentId == null) {
            // 根节点同时兼容 parent_id IS NULL 与 parent_id = 0
            wrapper.and(w -> w.isNull(Knowledge::getParentId)
                    .or()
                    .eq(Knowledge::getParentId, 0L));
        } else {
            wrapper.eq(Knowledge::getParentId, parentId);
        }
        wrapper.orderByAsc(Knowledge::getNodeType); // folder优先
        wrapper.orderByDesc(Knowledge::getUpdatedTime);
        IPage<Knowledge> knowledgePage = knowledgeMapper.selectPage(pageParam, wrapper);
        return knowledgePage.convert(this::convertToVO);
    }

    public IPage<KnowledgeVO> getChildrenFiltered(Long parentId, int page, int size, java.util.List<String> allowedWorkspaces) {
        if (allowedWorkspaces == null || allowedWorkspaces.isEmpty()) {
            return getChildren(parentId, page, size);
        }
        Page<Knowledge> pageParam = new Page<>(page, size);
        java.util.Set<Long> ids = knowledgeWorkspaceService.listKnowledgeIdsByWorkspaces(allowedWorkspaces);
        if (ids.isEmpty()) {
            Page<KnowledgeVO> empty = new Page<>(page, size);
            empty.setTotal(0);
            empty.setRecords(java.util.Collections.emptyList());
            return empty;
        }
        LambdaQueryWrapper<Knowledge> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Knowledge::getDeleted, 0).in(Knowledge::getId, ids);
        if (parentId == null) {
            wrapper.and(w -> w.isNull(Knowledge::getParentId).or().eq(Knowledge::getParentId, 0L));
        } else {
            wrapper.eq(Knowledge::getParentId, parentId);
        }
        wrapper.orderByAsc(Knowledge::getNodeType);
        wrapper.orderByDesc(Knowledge::getUpdatedTime);
        IPage<Knowledge> knowledgePage = knowledgeMapper.selectPage(pageParam, wrapper);
        return knowledgePage.convert(this::convertToVO);
    }

    /**
     * 递归构建知识树（谨慎使用：节点数大时建议分页/懒加载）
     */
    public List<com.knowledge.vo.KnowledgeTreeVO> getKnowledgeTree() {
        LambdaQueryWrapper<Knowledge> rootWrapper = new LambdaQueryWrapper<Knowledge>()
                .eq(Knowledge::getDeleted, 0)
                .and(w -> w.isNull(Knowledge::getParentId).or().eq(Knowledge::getParentId, 0L))
                .orderByAsc(Knowledge::getNodeType)
                .orderByDesc(Knowledge::getUpdatedTime);
        List<Knowledge> roots = knowledgeMapper.selectList(rootWrapper);
        return roots.stream().map(this::toTreeNode).collect(Collectors.toList());
    }

    private com.knowledge.vo.KnowledgeTreeVO toTreeNode(Knowledge k) {
        com.knowledge.vo.KnowledgeTreeVO node = new com.knowledge.vo.KnowledgeTreeVO();
        node.setId(k.getId());
        node.setName(k.getName());
        node.setParentId(k.getParentId());
        node.setNodeType(k.getNodeType());
        // 无论节点类型，均加载子节点，保证“文档型”节点也能作为容器显示其子项
        List<Knowledge> children = knowledgeMapper.selectList(new LambdaQueryWrapper<Knowledge>()
                .eq(Knowledge::getDeleted, 0)
                .eq(Knowledge::getParentId, k.getId())
                .orderByAsc(Knowledge::getNodeType)
                .orderByDesc(Knowledge::getUpdatedTime));
        node.setChildren(children.isEmpty() ? java.util.Collections.emptyList() : children.stream().map(this::toTreeNode).collect(Collectors.toList()));
        return node;
    }
    
    /**
     * 搜索知识
     */
    public IPage<KnowledgeVO> searchKnowledge(String query, int page, int size, java.util.List<String> allowedWorkspaces) {
        // 仅使用ES搜索，失败直接抛出异常
        // 传入页码与大小，由ES服务内部计算from/size
        List<com.knowledge.vo.ElasticsearchResultVO> esResults = elasticsearchService
            .searchKnowledge(query, page, size, allowedWorkspaces);

        List<KnowledgeVO> vos = esResults.stream()
            .map(esResult -> {
                KnowledgeVO vo = new KnowledgeVO();
                vo.setId(esResult.getId());
                vo.setName(esResult.getTitle());
                vo.setDescription(esResult.getContent());
                // 兼容：移除类目，ES不再返回categoryId
                if (esResult.getTags() != null) {
                    String tagsStr = esResult.getTags().trim();
                    if (!tagsStr.isEmpty()) {
                        vo.setTags(java.util.Arrays.asList(tagsStr.split(",")));
                    } else {
                        vo.setTags(java.util.Collections.emptyList());
                    }
                }
                vo.setCreatedBy(esResult.getAuthor());
                // 绑定的工作空间（从DB补齐）
                try {
                    vo.setWorkspaces(knowledgeWorkspaceService.listWorkspaces(vo.getId()));
                } catch (Exception ignore) {
                    vo.setWorkspaces(java.util.Collections.emptyList());
                }
                // 附件列表（从数据库补齐，前端需要展示）
                try {
                    List<Attachment> atts = attachmentService.getByKnowledgeId(vo.getId());
                    if (atts != null && !atts.isEmpty()) {
                        List<AttachmentVO> attVos = atts.stream().map(att -> {
                            AttachmentVO a = new AttachmentVO();
                            a.setId(att.getId());
                            a.setFileName(att.getFileName());
                            // 将filePath改为下载URL格式，与/api/chat/stream接口保持一致
                            a.setFilePath("/api/knowledge/" + vo.getId() + "/document/" + att.getId() + "/download");
                            a.setFileSize(att.getFileSize());
                            a.setFileType(att.getFileType());
                            a.setUploadTime(att.getUploadTime());
                            a.setDownloadCount(att.getDownloadCount());
                            return a;
                        }).collect(java.util.stream.Collectors.toList());
                        vo.setAttachments(attVos);
                    } else {
                        vo.setAttachments(java.util.Collections.emptyList());
                    }
                } catch (Exception ex) {
                    log.warn("搜索结果补齐附件失败: knowledgeId={}, error={}", vo.getId(), ex.getMessage());
                    vo.setAttachments(java.util.Collections.emptyList());
                }
                return vo;
            })
            .collect(Collectors.toList());

        Page<KnowledgeVO> result = new Page<>(page, size);
        result.setRecords(vos);
        result.setTotal(elasticsearchService.getSearchCount(query, allowedWorkspaces));
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
        wrapper.orderByDesc(Knowledge::getUpdatedTime);
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
        // 兼容：categoryId 赋值为 parentId，便于旧前端/测试平滑过渡
        vo.setCategoryId(knowledge.getParentId());
        // 绑定的工作空间
        try {
            vo.setWorkspaces(knowledgeWorkspaceService.listWorkspaces(knowledge.getId()));
        } catch (Exception ignore) {
            vo.setWorkspaces(java.util.Collections.emptyList());
        }
        // 附件列表填充
        try {
            List<Attachment> attachments = attachmentService.getByKnowledgeId(knowledge.getId());
            if (attachments != null && !attachments.isEmpty()) {
                List<AttachmentVO> attachmentVOS = attachments.stream().map(att -> {
                    AttachmentVO a = new AttachmentVO();
                    a.setId(att.getId());
                    a.setFileName(att.getFileName());
                    // 将filePath改为下载URL格式，与/api/chat/stream接口保持一致
                    a.setFilePath("/api/knowledge/" + knowledge.getId() + "/document/" + att.getId() + "/download");
                    a.setFileSize(att.getFileSize());
                    a.setFileType(att.getFileType());
                    a.setUploadTime(att.getUploadTime());
                    a.setDownloadCount(att.getDownloadCount());
                    return a;
                }).collect(java.util.stream.Collectors.toList());
                vo.setAttachments(attachmentVOS);
            } else {
                vo.setAttachments(java.util.Collections.emptyList());
            }
        } catch (Exception ex) {
            log.warn("获取附件列表失败: knowledgeId={}, error={}", knowledge.getId(), ex.getMessage());
            vo.setAttachments(java.util.Collections.emptyList());
        }
        // 点赞/收藏数量
        // 点赞/收藏数量可在专用接口查询，这里暂不填充
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
                knowledge.getTags() == null ? null : String.join(",", knowledge.getTags()),
                effectiveTime
            );

            // 同步保存附件，确保列表和详情能看到关联文件
            attachmentService.saveFiles(knowledgeId, new MultipartFile[]{file}, currentUser);

            // 更新ES中的知识索引，包含最新附件信息与workspaces
            List<Attachment> attachments = attachmentService.getByKnowledgeId(knowledgeId);
            java.util.List<String> workspaces = knowledgeWorkspaceService.listWorkspaces(knowledgeId);
            elasticsearchService.updateKnowledge(knowledge, attachments, workspaces);
            
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
