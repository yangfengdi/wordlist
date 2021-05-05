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

drop table remember_event;
create table IF NOT EXISTS remember_event (
  word text,
  remember_date date,
  create_time timestamp DEFAULT CURRENT_TIMESTAMP
);

drop table mistake_event;
create table IF NOT EXISTS mistake_event (
  word text,
  mistake_date date,
  create_time timestamp DEFAULT CURRENT_TIMESTAMP
);

-- 单词词频库
drop table word_freq;
create table IF NOT EXISTS word_freq (
  pos integer,
  word text,
  freq_type text
);

