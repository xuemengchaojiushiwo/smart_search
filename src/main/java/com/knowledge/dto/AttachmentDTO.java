package com.knowledge.dto;

import lombok.Data;

@Data
public class AttachmentDTO {

    private String fileName;

    private String filePath;

    private Long fileSize;

    private String fileType;
}
