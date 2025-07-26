CREATE TABLE execution_annotation_tags (
  annotationId INTEGER NOT NULL,
  tagId VARCHAR(24) NOT NULL,
  PRIMARY KEY (annotationId, tagId)
);