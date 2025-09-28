package com.knowledge.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.knowledge.entity.KnowledgeWorkspace;
import com.knowledge.mapper.KnowledgeWorkspaceMapper;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.List;

@Service
public class KnowledgeWorkspaceService extends ServiceImpl<KnowledgeWorkspaceMapper, KnowledgeWorkspace> {

    public List<String> listWorkspaces(Long knowledgeId) {
        if (knowledgeId == null) return Collections.emptyList();
        return baseMapper.listWorkspacesByKnowledgeId(knowledgeId);
    }

    public void replaceBindings(Long knowledgeId, List<String> workspaces) {
        // 删除旧绑定
        remove(new LambdaQueryWrapper<KnowledgeWorkspace>().eq(KnowledgeWorkspace::getKnowledgeId, knowledgeId));
        if (workspaces == null || workspaces.isEmpty()) return;
        // 批量新增
        for (String ws : workspaces) {
            if (ws == null || ws.trim().isEmpty()) continue;
            KnowledgeWorkspace kw = new KnowledgeWorkspace();
            kw.setKnowledgeId(knowledgeId);
            kw.setWorkspace(ws.trim());
            save(kw);
        }
    }

    public java.util.Set<Long> listKnowledgeIdsByWorkspaces(List<String> workspaces) {
        if (workspaces == null || workspaces.isEmpty()) return java.util.Collections.emptySet();
        
        // 构建查询条件：用户有权限的工作空间 OR ALL工作空间
        LambdaQueryWrapper<KnowledgeWorkspace> wrapper = new LambdaQueryWrapper<>();
        wrapper.and(w -> w.in(KnowledgeWorkspace::getWorkspace, workspaces)
                .or()
                .eq(KnowledgeWorkspace::getWorkspace, "ALL"));
        
        List<KnowledgeWorkspace> records = list(wrapper);
        if (records == null || records.isEmpty()) return java.util.Collections.emptySet();
        java.util.Set<Long> ids = new java.util.HashSet<>();
        for (KnowledgeWorkspace kw : records) {
            if (kw.getKnowledgeId() != null) ids.add(kw.getKnowledgeId());
        }
        return ids;
    }
    
    /**
     * 根据逗号分隔的工作空间字符串获取知识ID列表
     */
    public java.util.Set<Long> listKnowledgeIdsByWorkspaceString(String workspaceString) {
        if (workspaceString == null || workspaceString.trim().isEmpty()) {
            return java.util.Collections.emptySet();
        }
        
        // 解析逗号分隔的工作空间
        List<String> workspaces = java.util.Arrays.asList(workspaceString.split(","));
        workspaces = workspaces.stream()
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .collect(java.util.stream.Collectors.toList());
        
        return listKnowledgeIdsByWorkspaces(workspaces);
    }
}


