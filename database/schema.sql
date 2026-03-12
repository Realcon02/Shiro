create type target_type as enum ('works', 'teams', 'works_teams', 'branches_works');

create table if not exists works
(
    work_id  bigint        not null
        constraint works_pk
            primary key,
    name     varchar(1023) not null,
    rus_name varchar(1023),
    slug_url varchar(1023) not null
);

comment on table works is 'Таблица с информацией о произведениях';

create table if not exists teams
(
    team_id  bigint        not null
        constraint teams_pk
            primary key,
    slug_url varchar(1023) not null
);

comment on table teams is 'Таблица для slug_url команд';

create table if not exists works_teams
(
    id      bigserial
        constraint works_teams_pk
            primary key,
    work_id bigint not null
        constraint works_teams_works_work_id_fk
            references works,
    team_id bigint not null
        constraint works_teams_teams_team_id_fk
            references teams
);

comment on table works_teams is 'Таблица для подписок "Произведение от команды"';

create table if not exists branches_works
(
    branch_id bigint not null
        constraint branches_works_pk
            primary key,
    work_id   bigint not null
        constraint branches_works_works_work_id_fk
            references works
);

comment on table branches_works is 'Таблица для подписок "Ветка произведения"';

create table if not exists subscriptions
(
    id                bigserial
        constraint subscriptions_pk
            primary key,
    target_type       target_type                            not null,
    target_id         bigint                                 not null,
    newest_id_chapter bigint                                 not null,
    created_at        timestamp with time zone default now() not null
);

comment on table subscriptions is 'Таблица для подписок';

create index if not exists subscriptions_target_id_target_type_index
    on subscriptions (target_id, target_type);

create index if not exists subscriptions_target_type_target_id_index
    on subscriptions (target_type, target_id);

create table if not exists subscriptions_guilds
(
    subscription_id bigint                                 not null
        constraint subscriptions_guilds_subscriptions_id_fk
            references subscriptions,
    guild_id        bigint                                 not null,
    channel_id      bigint                                 not null,
    created_at      timestamp with time zone default now() not null,
    constraint subscriptions_guilds_pk
        primary key (subscription_id, guild_id)
);

comment on table subscriptions_guilds is 'Таблица отношений подписок к серверам';

create index if not exists subscriptions_guilds_guild_id_index
    on subscriptions_guilds (guild_id);

create index if not exists subscriptions_guilds_subscription_id_index
    on subscriptions_guilds (subscription_id);


