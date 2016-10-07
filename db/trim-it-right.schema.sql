CREATE TABLE game (
	id integer primary key,
	gameName text not null,
	user_id integer not null,
	date timestamp not null,
	score integer,
	duration numeric,
	success integer,
	foreign key(user_id) references user(id)
);
CREATE TABLE game_log (
	id integer primary key,
	game_id integer not null,
	timestamp numeric,
	angle numeric,
	foreign key(game_id) references game(id)
);
CREATE TABLE user (
	id integer primary key,
	name text not null,
	email text not null,
	initials text not null,
	created timestamp
);
CREATE TRIGGER tg_user_created AFTER INSERT ON user
BEGIN
	UPDATE user SET created = CURRENT_TIMESTAMP WHERE rowid = new.rowid;
END;
CREATE INDEX ix_game_success on game(success);
CREATE INDEX ix_game_duration on game(duration);
CREATE INDEX ix_game_score on game(score);
CREATE UNIQUE INDEX ix_user_email on user(email);
CREATE INDEX ix_user_initials on user(initials);
CREATE INDEX ix_user_name on user(name);
