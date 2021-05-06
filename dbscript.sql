--drop table dict;
create table IF NOT EXISTS dict (
  word text,
  meaning text,
  source text,
  create_time timestamp DEFAULT CURRENT_TIMESTAMP
);

--drop table word_mapping;
create table IF NOT EXISTS word_mapping (
  word text,
  target_word text,
  source text
);

--drop table word_tag;
create table IF NOT EXISTS word_tag (
  word text,
  tag text,
  create_time timestamp DEFAULT CURRENT_TIMESTAMP
);

--drop table remember_event;
create table IF NOT EXISTS remember_event (
  word text,
  remember_date date,
  create_time timestamp DEFAULT CURRENT_TIMESTAMP
);

--drop table quiz_event;
create table IF NOT EXISTS quiz_event (
  word text,
  quiz_date date,
  quiz_result text,
  create_time timestamp DEFAULT CURRENT_TIMESTAMP
);

-- 单词词频库
--drop table word_freq;
create table IF NOT EXISTS word_freq (
  pos integer,
  word text,
  freq_type text
);

