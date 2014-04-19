drop table if exists users;
create table users (
    id integer primary key autoincrement,
    username text not null,
    email text not null,
    pw_hash text not null
);
insert into users (username, email, pw_hash) values ('faria', 'faria.chowdhury@gmail.com', 'pbkdf2:sha1:1000$fFCo5fuL$d202caaa7ac080ce8da86de68445d6ca2c2f191f');
insert into users (username, email, pw_hash) values ('luis', 'luis.armendariz@gmail.com', 'pbkdf2:sha1:1000$JP44y6e6$eccfbc3d986c8598867a5bff978957b488fbeeb1');

drop table if exists fibs;
create table fibs (
    user_id integer not null,
    n integer not null,
    value text not null default '',
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- EOF
