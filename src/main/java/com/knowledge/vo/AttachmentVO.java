package com.knowledge.vo;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class AttachmentVO {

    private Long id;

    private String fileName;

    private String filePath;

    private Long fileSize;

    private String fileType;

    private LocalDateTime uploadTime;

    private Integer downloadCount;
}
