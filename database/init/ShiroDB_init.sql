--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: ShiroDB; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE "ShiroDB" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'ru-RU';


ALTER DATABASE "ShiroDB" OWNER TO postgres;

\connect "ShiroDB"

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: DATABASE "ShiroDB"; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON DATABASE "ShiroDB" IS 'Database for Discord bot Shiro';


--
-- Name: target_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.target_type AS ENUM (
    'works',
    'teams',
    'works_teams',
    'branches_works'
);


ALTER TYPE public.target_type OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: branches_works; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.branches_works (
    branch_id bigint NOT NULL,
    work_id bigint NOT NULL,
    branch_number smallint NOT NULL
);


ALTER TABLE public.branches_works OWNER TO postgres;

--
-- Name: TABLE branches_works; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.branches_works IS 'Таблица для подписок «Ветка произведения»';


--
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subscriptions (
    id bigint NOT NULL,
    target_type public.target_type NOT NULL,
    target_id bigint NOT NULL,
    newest_id_chapter bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.subscriptions OWNER TO postgres;

--
-- Name: TABLE subscriptions; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.subscriptions IS 'Таблица для подписок';


--
-- Name: subscriptions_guilds; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subscriptions_guilds (
    subscription_id bigint NOT NULL,
    guild_id bigint NOT NULL,
    channel_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.subscriptions_guilds OWNER TO postgres;

--
-- Name: TABLE subscriptions_guilds; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.subscriptions_guilds IS 'Таблица отношений подписок к серверам';


--
-- Name: subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.subscriptions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subscriptions_id_seq OWNER TO postgres;

--
-- Name: subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.subscriptions_id_seq OWNED BY public.subscriptions.id;


--
-- Name: teams; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teams (
    team_id bigint NOT NULL,
    name character varying(1023) NOT NULL,
    slug_url character varying(1023) NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.teams OWNER TO postgres;

--
-- Name: TABLE teams; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.teams IS 'Таблица с информацией о командах';


--
-- Name: works; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.works (
    work_id bigint NOT NULL,
    site_id smallint NOT NULL,
    name character varying(1023) NOT NULL,
    rus_name character varying(1023),
    slug_url character varying(1023) NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.works OWNER TO postgres;

--
-- Name: TABLE works; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.works IS 'Таблица с информацией о произведениях';


--
-- Name: works_teams; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.works_teams (
    id bigint NOT NULL,
    work_id bigint NOT NULL,
    team_id bigint NOT NULL
);


ALTER TABLE public.works_teams OWNER TO postgres;

--
-- Name: TABLE works_teams; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.works_teams IS 'Таблица для подписок «Произведение от команды»';


--
-- Name: works_teams_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.works_teams_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.works_teams_id_seq OWNER TO postgres;

--
-- Name: works_teams_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.works_teams_id_seq OWNED BY public.works_teams.id;


--
-- Name: subscriptions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriptions ALTER COLUMN id SET DEFAULT nextval('public.subscriptions_id_seq'::regclass);


--
-- Name: works_teams id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.works_teams ALTER COLUMN id SET DEFAULT nextval('public.works_teams_id_seq'::regclass);


--
-- Name: branches_works branches_works_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.branches_works
    ADD CONSTRAINT branches_works_pk PRIMARY KEY (branch_id);


--
-- Name: subscriptions_guilds subscriptions_guilds_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriptions_guilds
    ADD CONSTRAINT subscriptions_guilds_pk PRIMARY KEY (subscription_id, guild_id);


--
-- Name: subscriptions subscriptions_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pk PRIMARY KEY (id);


--
-- Name: teams teams_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_pk PRIMARY KEY (team_id);


--
-- Name: works works_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.works
    ADD CONSTRAINT works_pk PRIMARY KEY (work_id);


--
-- Name: works_teams works_teams_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.works_teams
    ADD CONSTRAINT works_teams_pk PRIMARY KEY (id);


--
-- Name: subscriptions_guilds_guild_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX subscriptions_guilds_guild_id_index ON public.subscriptions_guilds USING btree (guild_id);


--
-- Name: subscriptions_guilds_subscription_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX subscriptions_guilds_subscription_id_index ON public.subscriptions_guilds USING btree (subscription_id);


--
-- Name: subscriptions_target_id_target_type_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX subscriptions_target_id_target_type_index ON public.subscriptions USING btree (target_id, target_type);


--
-- Name: subscriptions_target_type_target_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX subscriptions_target_type_target_id_index ON public.subscriptions USING btree (target_type, target_id);


--
-- Name: branches_works branches_works_works_work_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.branches_works
    ADD CONSTRAINT branches_works_works_work_id_fk FOREIGN KEY (work_id) REFERENCES public.works(work_id);


--
-- Name: subscriptions_guilds subscriptions_guilds_subscriptions_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriptions_guilds
    ADD CONSTRAINT subscriptions_guilds_subscriptions_id_fk FOREIGN KEY (subscription_id) REFERENCES public.subscriptions(id);


--
-- Name: works_teams works_teams_teams_team_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.works_teams
    ADD CONSTRAINT works_teams_teams_team_id_fk FOREIGN KEY (team_id) REFERENCES public.teams(team_id);


--
-- Name: works_teams works_teams_works_work_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.works_teams
    ADD CONSTRAINT works_teams_works_work_id_fk FOREIGN KEY (work_id) REFERENCES public.works(work_id);


--
-- PostgreSQL database dump complete
--

