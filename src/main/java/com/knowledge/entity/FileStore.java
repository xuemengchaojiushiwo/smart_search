package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("file_store")
public class FileStore {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String originalName;
    private String mime;
    private Long size;
    private String pathOriginal;
    private String pathPdf;
    private String status; // UPLOADED, PROCESSED, FAILED
}


