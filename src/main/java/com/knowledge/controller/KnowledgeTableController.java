// package com.knowledge.controller;
//
// import com.knowledge.entity.*;
// import com.knowledge.exception.BusinessException;
// import com.knowledge.service.*;
// import lombok.Data;
// import lombok.RequiredArgsConstructor;
// import org.springframework.http.MediaType;
// import org.springframework.web.bind.annotation.*;
// import org.springframework.web.multipart.MultipartFile;
//
// import java.io.File;
// import java.io.IOException;
// import java.util.List;
//
// @RestController
// @RequestMapping("/api/knowledge")
// @RequiredArgsConstructor
// public class KnowledgeTableController {
//     private final KnowledgeTableService tableService;
//     private final KnowledgeColumnService columnService;
//     private final KnowledgeRowService rowService;
//     private final KnowledgeCellService cellService;
//     private final FileStoreService fileStoreService;
//     private final KnowledgeService knowledgeService;
//
//     @GetMapping("/tables/{tableId}")
//     public KnowledgeTable getTable(@PathVariable Long tableId) {
//         KnowledgeTable t = tableService.getById(tableId);
//         if (t == null) throw new BusinessException("表不存在");
//         return t;
//     }
//
//     @GetMapping("/tables/{tableId}/columns")
//     public List<KnowledgeColumn> listColumns(@PathVariable Long tableId) {
//         return columnService.lambdaQuery().eq(KnowledgeColumn::getTableId, tableId).orderByAsc(KnowledgeColumn::getSortOrder).list();
//     }
//
//     @GetMapping("/tables/{tableId}/rows")
//     public List<KnowledgeRow> listRows(@PathVariable Long tableId) {
//         return rowService.lambdaQuery().eq(KnowledgeRow::getTableId, tableId).list();
//     }
//
//     @GetMapping("/rows/{rowId}/cells")
//     public List<KnowledgeCell> listCells(@PathVariable Long rowId) {
//         return cellService.lambdaQuery().eq(KnowledgeCell::getRowId, rowId).list();
//     }
//
//     @PostMapping("/tables")
//     public KnowledgeTable createTable(@RequestBody CreateTableReq req) {
//         KnowledgeTable t = new KnowledgeTable();
//         t.setName(req.getName());
//         t.setOwnerId(req.getOwnerId());
//         t.setDept(req.getDept());
//         tableService.save(t);
//         return t;
//     }
//
//     @PostMapping("/tables/{tableId}/columns")
//     public KnowledgeColumn addColumn(@PathVariable Long tableId, @RequestBody AddColumnReq req) {
//         KnowledgeColumn c = new KnowledgeColumn();
//         c.setTableId(tableId);
//         c.setName(req.getName());
//         c.setType(req.getType());
//         c.setRequired(Boolean.TRUE.equals(req.getRequired()));
//         c.setSortOrder(req.getSortOrder() == null ? 0 : req.getSortOrder());
//         columnService.save(c);
//         return c;
//     }
//
//     @PostMapping("/tables/{tableId}/rows")
//     public KnowledgeRow addRow(@PathVariable Long tableId, @RequestBody AddRowReq req) {
//         KnowledgeRow r = new KnowledgeRow();
//         r.setTableId(tableId);
//         r.setCreatedBy(req.getCreatedBy());
//         rowService.save(r);
//         return r;
//     }
//
//     @PutMapping("/cells/{cellId}")
//     public KnowledgeCell updateCell(@PathVariable Long cellId, @RequestBody UpdateCellReq req) {
//         KnowledgeCell c = cellService.getById(cellId);
//         if (c == null) throw new BusinessException("单元格不存在");
//         if (req.getTextValue() != null) c.setTextValue(req.getTextValue());
//         if (req.getLinkUrl() != null) c.setLinkUrl(req.getLinkUrl());
//         cellService.updateById(c);
//         return c;
//     }
//
//     @PostMapping(value = "/cells/{cellId}/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
//     public KnowledgeCell uploadCellFile(@PathVariable Long cellId, @RequestParam("file") MultipartFile file,
//                                         @RequestParam("knowledgeId") Long knowledgeId) throws IOException {
//         KnowledgeCell c = cellService.getById(cellId);
//         if (c == null) throw new BusinessException("单元格不存在");
//
//         // 1) 保存原文件
//         File dir = new File("uploads/original");
//         if (!dir.exists()) dir.mkdirs();
//         File saved = new File(dir, file.getOriginalFilename());
//         file.transferTo(saved);
//
//         FileStore fs = new FileStore();
//         fs.setOriginalName(file.getOriginalFilename());
//         fs.setMime(file.getContentType());
//         fs.setSize(file.getSize());
//         fs.setPathOriginal(saved.getAbsolutePath());
//         fs.setStatus("UPLOADED");
//         fileStoreService.save(fs);
//
//         // 2) 调用现有知识处理，写入 ES（保持原文件不改，PDF 仅用于展示）
//         // 这里直接复用 KnowledgeService 的 processKnowledgeDocument
//         knowledgeService.processKnowledgeDocument(file, knowledgeId, "system");
//
//         // 3) 简化：此处不存 pathPdf，待 Python 成功后由异步回填也可
//         c.setFileId(fs.getId());
//         cellService.updateById(c);
//         return c;
//     }
//
//     // DTOs
//     @Data
//     public static class CreateTableReq { private String name; private Long ownerId; private String dept; }
//     @Data
//     public static class AddColumnReq { private String name; private String type; private Boolean required; private Integer sortOrder; }
//     @Data
//     public static class AddRowReq { private Long createdBy; }
//     @Data
//     public static class UpdateCellReq { private String textValue; private String linkUrl; }
// }
//
//
