--drop table dict;
create table IF NOT EXISTS dict (
  word text,
  meaning text,
  source text,
  create_time timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_dict_word on dict (word);

--drop table word_mapping;
create table IF NOT EXISTS word_mapping (
  word text,
  target_word text,
  source text
);
CREATE INDEX idx_word_mapping_word on word_mapping (word);

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

-- 单词记忆计划表
-- drop table word_remember_plan;
create table IF NOT EXISTS word_remember_plan (
  word text,
  word_type text,
  seq_no integer,
  gap_days integer,
  plan_status text,
  plan_remember_date date,
  ideal_remember_date date,
  create_time timestamp DEFAULT CURRENT_TIMESTAMP
);
-- 评价单词记忆计划的效果，可以通过看实际计划时间与理想时间的偏差来评估
select julianday(plan_remember_date) - julianday(ideal_remember_date) gap, count(1)
from word_remember_plan a group by gap;
-- 查看每天计划的单词量，看是不是每天都按照计划排满了，偏后段的时间，随着单词接近背完，每天的背诵量可能不会被排满
select plan_remember_date, count(1) from word_remember_plan
group by plan_remember_date;
-- 计划重排前的初始化
