package com.knowledge.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.knowledge.entity.Workspace;
import com.knowledge.mapper.WorkspaceMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class WorkspaceService {
    private final WorkspaceMapper mapper;

    public Workspace create(String code, String name, String description) {
        Workspace exist = mapper.selectOne(new LambdaQueryWrapper<Workspace>()
                .eq(Workspace::getCode, code));
        if (exist != null) return exist;
        Workspace ws = new Workspace();
        ws.setCode(code);
        ws.setName(name == null || name.isEmpty() ? code : name);
        ws.setDescription(description);
        ws.setCreatedTime(LocalDateTime.now());
        mapper.insert(ws);
        return ws;
    }

    public List<Workspace> listAll() {
        return mapper.selectList(new LambdaQueryWrapper<Workspace>().orderByAsc(Workspace::getCode));
    }
}


