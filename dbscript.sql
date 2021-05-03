drop table dict;
create table IF NOT EXISTS dict (
word text,
meaning text,
source text,
create_time timestamp DEFAULT CURRENT_TIMESTAMP
);

drop table word_tag;
create table IF NOT EXISTS word_tag (
word text,
tag text,
create_time timestamp DEFAULT CURRENT_TIMESTAMP
);
